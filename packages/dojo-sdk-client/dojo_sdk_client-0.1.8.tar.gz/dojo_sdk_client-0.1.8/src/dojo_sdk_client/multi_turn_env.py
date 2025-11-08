import asyncio
import atexit
import base64
import json
import logging
import os
import time
from io import BytesIO
from typing import Any, List, Tuple

import verifiers as vf
from datasets import Dataset
from dojo_sdk_core.settings import settings
from dojo_sdk_core.tasks import RemoteTaskLoader
from dojo_sdk_core.types import (
    Action,
    ClickAction,
    WaitAction,
)
from verifiers.types import Message, Messages, State

from .agents.anthropic_cua import SYSTEM_PROMPT
from .agents.computer_use_tool import computer_tool
from .base_dojo_client import NoRunnersAvailableError, TaskStatus
from .engines import Engine, select_engine
from .utils import load_tasks_from_hf_dataset

logger = logging.getLogger(__name__)


def load_benchmark_tasks(tasks: List[str], task_loader: RemoteTaskLoader, system_prompt: str) -> Dataset:
    dataset_rows = []
    for task_id in tasks:
        task = task_loader.load_task(task_id)
        dataset_rows.append(
            {
                "prompt": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": task.instructions.user_prompt},
                ],
                "answer": "",
                "task": task.name,
                "info": {
                    "task_id": task_id,
                    "task_name": task.name,
                    "initial_state": json.dumps(task.initial_state),
                    "max_steps": task.max_steps,
                },
            }
        )

    return Dataset.from_list(dataset_rows)


class DojoReward(vf.RewardFunc):
    def __init__(self, engine: Engine, task_loader: RemoteTaskLoader, verbose: bool = False):
        self.client = engine
        self.verbose = verbose
        self.task_loader = task_loader

    @property
    def __name__(self) -> str:
        return "DojoReward"

    async def __call__(self, **kwargs: Any) -> float:
        state = kwargs.get("state", None)
        exec_id = state.get("exec_id", None)
        if not exec_id:
            logger.error("No exec_id found in state")
            return 0.0

        task_id = state.get("task_id", None)
        if not task_id:
            logger.error("No task_id found in state")
            return 0.0

        # Get the final task state from the server
        task_response = await self.client.get_task_status(exec_id)

        # Load the task definition to get its reward function
        task_def = self.task_loader.load_task(task_id)

        # Call the task's reward function
        reward_function = task_def.load_reward_function()
        initial_state = json.loads(state.get("initial_state", "{}"))
        final_score, reason = reward_function(initial_state, task_response.state)

        if self.verbose:
            logger.info(f"Task {exec_id} ({task_id}) reward: {final_score:.2f} - {reason}")

        return final_score


class DojoMultiTurnEnv(vf.ToolEnv):
    def __init__(
        self,
        engine: Engine,
        dataset: Dataset,
        task_loader: RemoteTaskLoader,
        **kwargs,
    ):
        self.client = engine
        self.task_loader = task_loader
        self._created_time = time.time()
        self.verbose = kwargs.get("verbose", False)
        # Track all active exec_ids
        self.active_exec_ids = set()
        self._cleanup_done = False
        super().__init__(dataset=dataset, **kwargs, tools=[computer_tool])
        atexit.register(self.cleanup)

    async def setup_state(self, state: State, **kwargs) -> State:
        info = state.get("info")

        state["task_id"] = info.get("task_id")
        state["initial_state"] = info.get("initial_state")
        state["max_steps"] = min(self.max_turns, info.get("max_steps"))
        state["step"] = 1
        state["started"] = False
        state["created"] = False

        return state

    async def _parse_tool_calls(self, messages: Messages) -> Tuple[List[Action], List[Message]]:
        actions = []
        tool_messages = []
        if "tool_calls" in messages[-1]:
            for tool_call in messages[-1]["tool_calls"]:
                tool_name: str = tool_call.function.name
                tool_args: dict = json.loads(tool_call.function.arguments)
                tool_call_id: str = tool_call.id or ""
                tool_message: Message = await self.call_tool(tool_name, tool_args, tool_call_id)
                tool_messages.append(tool_message)
                try:
                    action = computer_tool(**tool_args)
                    actions.append(action)
                except Exception as e:
                    logger.error(f"Error in computer_tool: {e} falling back to click")
                    action = ClickAction(x=100, y=100)
        return actions, tool_messages

    async def env_response(self, messages: Messages, state: State, **kwargs: Any) -> Tuple[Messages, State]:
        created = state.get("created", False)

        if not created:
            exec_id = await self.client.create_task(state["task_id"], json.loads(state["initial_state"]), metadata={})
            state["exec_id"] = exec_id
            state["created"] = True
            # Track this exec_id
            self.active_exec_ids.add(exec_id)
            if self.verbose:
                logger.info(f"Created task {state['task_id']}")

        exec_id = state.get("exec_id")
        if not exec_id:
            raise ValueError("Execution ID not found in state")

        while not state.get("started", False):
            # Start the task using DojoClient
            try:
                await self.client.start_task(exec_id=state.get("exec_id"))
            except NoRunnersAvailableError:
                if self.verbose:
                    logger.error("No runners available, retrying in 2 seconds")
                await asyncio.sleep(2)
                continue
            except Exception as e:
                logger.error(f"Error starting task {state['exec_id']}: {e}")
                raise e
            logger.info(f"Started task {state['exec_id']}")

            state["started"] = True

            result = await self.client.get_task_status(exec_id)
            while result.status is TaskStatus.QUEUED:
                if self.verbose:
                    logger.info(f"Task {exec_id} is queued, retrying in 1 second")
                await asyncio.sleep(1)
                result = await self.client.get_task_status(exec_id)

        assert isinstance(messages[-1], dict)
        last_message = messages[-1]["content"]
        if not last_message or last_message.strip() == "":
            for message in messages[::-1]:
                last_message = message["content"]
                break

        assert isinstance(messages, list)
        actions, tool_messages = await self._parse_tool_calls(messages)
        if self.verbose:
            logger.info(f"Last message: {last_message} actions: {actions}")

        if len(actions) == 0:
            actions = [WaitAction()]

        if self.verbose:
            logger.info(f"Step: {state.get('step', 0)} Max steps: {state.get('max_steps', 15)}")

        # Submit action using DojoClient
        await self.client.submit_action(
            exec_id=exec_id,
            action=actions[0].model_dump(),
            agent_response=str(last_message),
            raw_response=json.dumps(last_message),
        )

        task_response = await self.client.get_task_status(exec_id)

        # Calculate and submit step score
        try:
            task_id = state.get("task_id")
            task_def = self.task_loader.load_task(task_id)
            reward_function = task_def.load_reward_function()
            initial_state = json.loads(state.get("initial_state", "{}"))
            step_score, reason = reward_function(initial_state, task_response.state)

            await self.client.submit_step_score(exec_id, task_response.step - 1, step_score)
            if self.verbose:
                logger.info(f"Step {task_response.step} score: {step_score:.2f} - {reason}")
        except Exception as e:
            logger.error(f"Failed to calculate/submit step score for task {exec_id}: {e}")

        screenshot_path = task_response.screenshot
        history = task_response.history

        state["step"] = task_response.step
        state["history"] = history

        # Get the image from the server
        image = await self.client.get_image(screenshot_path)

        buffer = BytesIO()
        image.save(buffer, format="PNG")
        screenshot_bytes = buffer.getvalue()
        b64_img = base64.b64encode(screenshot_bytes).decode("utf-8")

        response_messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{b64_img}"},
                    }
                ],
            }
        ]

        if self.verbose:
            logger.info(f"Environment responded for task {exec_id} with step {state['step']}")

        return tool_messages + response_messages, state

    async def is_completed(self, messages: Messages, state: State, **kwargs: Any) -> bool:
        """Check if the task is completed."""
        created = state.get("created", False)
        if not created:
            return False

        if not state.get("started", False):
            return False

        exec_id = state.get("exec_id", None)
        if not exec_id:
            raise ValueError("Execution ID not found in state")

        if state.get("step", 0) >= state.get("max_steps", 15):
            await self.client.stop_task(exec_id, status=TaskStatus.COMPLETED)
            # Remove from active set
            self.active_exec_ids.discard(exec_id)
            return True

        # Check task status
        task_response = await self.client.get_task_status(exec_id)
        is_finished = task_response.status in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELED)
        # logger.info(f"Task {exec_id} is finished: {is_finished}")
        if is_finished:
            await self.client.stop_task(exec_id, status=TaskStatus.COMPLETED)
            self.active_exec_ids.discard(exec_id)
        return is_finished

    def cleanup(self):
        """Cleanup method called on exit. Stops all active tasks."""
        if self._cleanup_done:
            return
        self._cleanup_done = True

        if self.active_exec_ids:
            logger.info(f"Cleaning up {len(self.active_exec_ids)} active tasks")
            for exec_id in self.active_exec_ids:
                logger.info(f"Stopping task {exec_id}")
                try:
                    self.client.stop_task_sync(exec_id, TaskStatus.CANCELED)
                except Exception as e:
                    logger.error(f"Error stopping task {exec_id}: {e}")
                    continue
            self.active_exec_ids.clear()


def load_environment(API_KEY: str, system_prompt: str, tasks: List[str], **kwargs):
    """Load the Dojo environment. The environment must be executed within a minute or it will be terminated."""

    # Load execution engine
    engine = select_engine(API_KEY)

    # Create all tasks
    task_loader = RemoteTaskLoader("chakra-labs/dojo-bench-mini")
    tasks_dataset = load_benchmark_tasks(tasks, task_loader, system_prompt)

    rubric = vf.Rubric(
        funcs=[DojoReward(engine, task_loader)],
        weights=[1.0],
    )

    env = DojoMultiTurnEnv(
        engine=engine,
        dataset=tasks_dataset,
        task_loader=task_loader,  # Add this parameter
        max_turns=15,
        rubric=rubric,
        **kwargs,
    )

    return env


def main():
    from openai import AsyncOpenAI

    tasks = load_tasks_from_hf_dataset("chakra-labs/dojo-bench-mini")

    API_KEY = os.getenv("DOJO_API_KEY")
    env = load_environment(
        API_KEY=API_KEY,
        system_prompt=SYSTEM_PROMPT
        + (
            "\n\nScreenshots are always provided as input. DO NOT ASK FOR A SCREENSHOT OR TRY TO TAKE A SCREENSHOT. "
            "DO NOT ASK FOR ANY INSTRUCTION FROM THE USER. When you are done, you must use the done action. "
            "Always perform an action"
        ),
        tasks=tasks[:2],
    )

    client = AsyncOpenAI(api_key=settings.anthropic_api_key, base_url="https://api.anthropic.com/v1/")
    eval_result = env.evaluate(
        client=client,
        model="claude-4-sonnet-20250514",
    )
    print(f"Task: {eval_result.task}")
    print(f"Metrics: {eval_result.metrics}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
