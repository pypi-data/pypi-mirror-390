import asyncio
import atexit
import logging
import traceback
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

from dojo_sdk_core import Action, ActionType, RemoteTaskLoader, TaskDefinition
from dojo_sdk_core.ws_types import HistoryStep
from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm

from .agents.base_agent import BaseAgent
from .engines.engine import Engine
from .telemetry.dojo_telemetry import telemetry
from .types import NoRunnersAvailableError, TaskResponse, TaskStatus

logger = logging.getLogger(__name__)


class MessageType(Enum):
    SUCCESS = "success"
    FAILED = "failed"
    ERROR = "error"


@dataclass
class WorkerMessage:
    type: MessageType
    exec_id: str
    task_response: Optional[TaskResponse] = None
    error: Optional[str] = None


@dataclass
class StepReward:
    step: int
    reward: float
    reason: str


@dataclass
class TaskMetadata:
    task_id: str
    exec_id: str
    task_definition: TaskDefinition
    current_step: int = 0
    step_rewards: list = None
    cleanup_done: bool = False

    def __post_init__(self):
        if self.step_rewards is None:
            self.step_rewards = []


@dataclass
class EvaluationResult:
    task_id: str
    task_name: str
    score: float
    reason: str
    step_rewards: List[StepReward]
    status: TaskStatus
    total_steps: int
    error: Optional[str] = None


class DojoEvalClient:
    """High-level client for running evaluations"""

    def __init__(self, agent: BaseAgent, verbose: bool = False, engine: Engine = None):
        self.agent = agent
        self.engine = engine
        self.task_loader = RemoteTaskLoader(dataset_name="chakra-labs/dojo-bench-mini")

        self.task_metadata: dict[str, TaskMetadata] = {}  # exec_id -> metadata
        self.verbose = verbose

        # Cleanup tasks on early exit to prevent orphaned tasks
        atexit.register(self._sync_cleanup)

    async def evaluate(self, tasks: list[str], num_runners: int = 1) -> List[EvaluationResult]:
        """
        Evaluate a list of tasks, respecting runner_limit.
        Tasks are queued and started as previous tasks complete.
        Returns list of evaluation results with task_id, task_name, score, and reason.
        """

        # Create all tasks concurrently
        exec_ids = await asyncio.gather(*[self._create_task(task_id) for task_id in tasks])
        logger.info(f"Created {len(exec_ids)} tasks concurrently")

        pending_queue = asyncio.Queue()
        result_queue = asyncio.Queue()

        # Populate work queue
        for exec_id in exec_ids:
            await pending_queue.put(exec_id)

        # Start result processor
        processor_task = asyncio.create_task(self._result_processor(result_queue, len(tasks)))

        # Start initial batch of workers up to runner_limit
        workers = [
            asyncio.create_task(self._worker(pending_queue, result_queue)) for _ in range(min(num_runners, len(exec_ids)))
        ]

        # Wait for all workers to complete
        await asyncio.gather(*workers)
        await pending_queue.join()

        # Signal processor to finish and get results
        await result_queue.put(None)
        completed_tasks = await processor_task

        # At the end, transform completed_tasks to EvaluationResults
        results = []
        for exec_id, task_response, error in completed_tasks:
            metadata = self.task_metadata[exec_id]
            task_def = metadata.task_definition

            if error or task_response.status == TaskStatus.FAILED:
                error_detail = error or task_response.error_detail or "Unknown error"
                # Task errored
                results.append(
                    EvaluationResult(
                        task_id=metadata.task_id,
                        task_name=task_def.name,
                        score=0.0,
                        reason="",
                        step_rewards=metadata.step_rewards,
                        status=TaskStatus.FAILED,
                        total_steps=len(metadata.step_rewards),
                        error=error_detail,
                    )
                )
            else:
                # Calculate final score
                reward_function = task_def.load_reward_function()

                if self.verbose:
                    logger.info(f"task_response.state: {task_response.state}")
                    logger.info(f"task_def.initial_state: {task_def.initial_state}")

                final_score, reason = reward_function(task_def.initial_state, self._sanitize_state(task_response.state))

                results.append(
                    EvaluationResult(
                        task_id=metadata.task_id,
                        task_name=task_def.name,
                        score=final_score,
                        reason=reason,
                        step_rewards=metadata.step_rewards,
                        status=task_response.status,
                        total_steps=len(metadata.step_rewards),
                    )
                )

        self._print_results(results)
        return results

    def _sanitize_state(self, state: Optional[dict]) -> dict:
        if state is None:
            return {}
        return state

    def _print_results(self, results: List[EvaluationResult]) -> str:
        """Format the results as a string"""
        failures = [r for r in results if r.score == 0.0 and not r.error]
        errors = [r for r in results if r.error]
        partial_successes = [r for r in results if r.score < 1.0 and r.score > 0.0]
        successes = [r for r in results if r.score == 1.0]

        results_str = "\n"

        if failures:
            results_str += "Failure details:\n"
            for result in failures:
                results_str += (
                    f"\t\t- {result.task_name} -> Status: {result.status.value} "
                    f"score: {result.score} reason: {result.reason} steps:{result.total_steps}\n"
                )
        if partial_successes:
            results_str += "Partial success details:\n"
            for result in partial_successes:
                results_str += (
                    f"\t\t- {result.task_name} -> Status: {result.status.value} "
                    f"score: {result.score} reason: {result.reason} steps:{result.total_steps}\n"
                )

        if errors:
            results_str += "Errors:\n"
            for result in errors:
                results_str += f"\t\t- {result.task_name} -> Error: {result.error}\n"

        # Summary line
        if results_str:
            results_str += "\n"

        percentage = int((len(successes) / len(results)) * 100) if len(results) > 0 else 0
        results_str += f"Score {percentage}% ({len(successes)}/{len(results)})"
        if partial_successes:
            results_str += f" | {len(partial_successes)} task{'s' if len(partial_successes) != 1 else ''} partially succeeded"
        errors_count = len(errors)
        if errors_count > 0:
            results_str += f" | {errors_count} task{'s' if errors_count != 1 else ''} errored"

        print(results_str)

    async def _create_task(self, task_id: str) -> str:
        """Create a task and store its metadata"""
        task_def = self.task_loader.load_task(task_id)

        exec_id = await self.engine.create_task(
            task_id=task_id,
            state=task_def.initial_state,
            metadata={},
        )

        # Store metadata for tracking
        self.task_metadata[exec_id] = TaskMetadata(task_id=task_id, exec_id=exec_id, task_definition=task_def, current_step=0)

        return exec_id

    async def _worker(self, pending_queue: asyncio.Queue, result_queue: asyncio.Queue):
        """Worker that processes tasks and sends results via message queue"""
        while True:
            try:
                exec_id = pending_queue.get_nowait()
            except asyncio.QueueEmpty:
                break

            try:
                task_state, task_successful = await self._run_task(exec_id)

                # Determine message type based on task outcome
                if task_successful:
                    message_type = MessageType.SUCCESS
                else:
                    message_type = MessageType.FAILED

                # Send result message to processor
                await result_queue.put(WorkerMessage(type=message_type, exec_id=exec_id, task_response=task_state))

            except Exception as e:
                logger.error(f"Error in worker for task {exec_id}: {e} {traceback.format_exc()}")
                # Send error message to processor
                await result_queue.put(WorkerMessage(type=MessageType.ERROR, exec_id=exec_id, error=str(e)))

                await self._try_terminate_task(exec_id, TaskStatus.FAILED)

            finally:
                pending_queue.task_done()

    async def _submit_action(self, task_def, metadata, exec_id, action, reasoning, raw_response) -> (TaskResponse, float):
        # submit action
        await self.engine.submit_action(exec_id, action.model_dump(), reasoning, raw_response)

        # wait for it to apply
        task_state = await self.engine.get_task_status(exec_id)
        while task_state.status is TaskStatus.RUNNING and task_state.step == metadata.current_step:
            await asyncio.sleep(0.5)
            task_state = await self.engine.get_task_status(exec_id)

        if task_state.status is not TaskStatus.RUNNING:
            return task_state, 0.0

        if self.verbose:
            logger.info(f"task_state.state: {task_state.state}")

        # Calculate step reward
        reward_function = task_def.load_reward_function()
        reward, reason = reward_function(task_def.initial_state, self._sanitize_state(task_state.state))

        # Save the step reward
        await self.engine.submit_step_score(exec_id, metadata.current_step, reward)
        metadata.step_rewards.append(StepReward(step=metadata.current_step, reward=reward, reason=reason))

        if self.verbose:
            logger.info(
                f"Task {exec_id} at step {metadata.current_step}/{task_def.max_steps} with reward {reward} and reason {reason}"
            )

        return task_state, reward

    async def _run_task(self, exec_id: str) -> tuple[TaskResponse, bool]:
        """Execute a single task from start to completion"""
        metadata = self.task_metadata[exec_id]
        task_def = metadata.task_definition

        if self.verbose:
            logger.info(f"Starting task {exec_id} ({metadata.task_id})")

        while True:
            try:
                await self.engine.start_task(exec_id)
                break
            except NoRunnersAvailableError:
                if self.verbose:
                    logger.warning(f"Task capacity reached for exec id {exec_id} and task id {metadata.task_id}, will retry")
                await asyncio.sleep(10)

        if self.verbose:
            logger.info(f"Started task {exec_id} ({metadata.task_id})")

        task_state = await self.engine.get_task_status(exec_id)

        # wait for task to be ready
        while task_state.status is TaskStatus.QUEUED:
            await asyncio.sleep(0.5)
            task_state = await self.engine.get_task_status(exec_id)

        metadata.current_step = task_state.step
        task_successful = False

        # Poll and execute actions until completion
        while task_state.status is TaskStatus.RUNNING:
            if self.verbose:
                logger.info(f"Getting next action for task {exec_id}")
            action, reasoning, raw_response = await self._get_agent_action(
                task_state.history or [], task_def.instructions.user_prompt, task_state.screenshot
            )

            task_state, last_score = await self._submit_action(task_def, metadata, exec_id, action, reasoning, raw_response)

            if task_state.status == TaskStatus.FAILED:
                await telemetry.send_event_async(
                    "task_failed", {"exec_id": exec_id, "task_id": metadata.task_id, "error_detail": task_state.error_detail}
                )
                break
            elif task_state.status is TaskStatus.CANCELED:
                break

            task_successful = last_score == 1.0

            if action.type == ActionType.DONE:
                break

            if metadata.current_step >= task_def.max_steps:
                if self.verbose:
                    logger.warning(f"Task {exec_id} reached max steps ({task_def.max_steps})")
                break

            metadata.current_step = task_state.step

        if task_state.status != TaskStatus.FAILED:
            await self._try_terminate_task(exec_id, TaskStatus.COMPLETED)
        metadata.cleanup_done = True

        if self.verbose:
            logger.info(f"Completed task {exec_id} ({metadata.task_id}) with status {task_state.status}")

        return task_state, task_successful

    async def _result_processor(self, result_queue: asyncio.Queue, total_tasks: int) -> list:
        """Handles state updates for tasks"""
        success_count = 0
        failed_count = 0
        error_count = 0
        completed_tasks = []

        pbar = tqdm(total=total_tasks, desc="Evaluating tasks", unit="task", leave=True, position=0, ncols=120)

        with logging_redirect_tqdm():
            while True:
                message = await result_queue.get()

                # Sentinel value to mark finish
                if message is None:
                    break

                # Handle all state updates sequentially
                match message.type:
                    case MessageType.SUCCESS:
                        success_count += 1
                        completed_tasks.append((message.exec_id, message.task_response, None))
                        pbar.update(1)

                    case MessageType.FAILED:
                        failed_count += 1
                        completed_tasks.append((message.exec_id, message.task_response, None))
                        pbar.update(1)

                    case MessageType.ERROR:
                        error_count += 1
                        completed_tasks.append((message.exec_id, None, message.error))
                        pbar.update(1)

                pbar.set_postfix({"✓": success_count, "✗": failed_count, "!": error_count})

                result_queue.task_done()

        pbar.close()
        return completed_tasks

    async def _get_agent_action(
        self, history: List[HistoryStep], prompt: str, screenshot_path: str
    ) -> tuple[Action, str, Optional[str]]:
        """Get next action from agent"""
        screenshot = await self.engine.get_image(screenshot_path)

        # Run synchronous agent method in thread pool to avoid blocking the event loop
        loop = asyncio.get_event_loop()
        action, reasoning, raw_response = await loop.run_in_executor(
            None,  # Uses default ThreadPoolExecutor
            self.agent.get_next_action,
            prompt,
            screenshot,
            history,
        )

        return action, reasoning, raw_response

    async def _try_terminate_task(self, exec_id: str, reason: TaskStatus) -> None:
        """
        Attempts to terminate a task

        If successful, marks the task as cleaned up.
        """
        try:
            await self.engine.stop_task(exec_id, reason)
            self.task_metadata[exec_id].cleanup_done = True
        except Exception:
            logger.debug(f"Failed to mark task {exec_id} as {reason}. trackback: {traceback.format_exc()}")

    def _sync_cleanup(self) -> None:
        """Synchronous cleanup wrapper for atexit"""
        if not self.task_metadata:
            return

        # active_exec_ids = list(self.task_metadata.keys())
        cleanup_tasks = [exec_id for exec_id in self.task_metadata.keys() if not self.task_metadata[exec_id].cleanup_done]

        if len(cleanup_tasks) == 0:
            return

        logger.info(f"Cleaning up {len(cleanup_tasks)} tasks...")

        # Use synchronous requests to cause async loop dies before cleanup
        for exec_id in cleanup_tasks:
            logger.info(f"Cleaning up task {exec_id}")
            try:
                self.engine.stop_task_sync(exec_id, TaskStatus.CANCELED)
            except Exception:
                logger.debug(f"Failed to cleanup task {exec_id}")
        self.task_metadata.clear()
