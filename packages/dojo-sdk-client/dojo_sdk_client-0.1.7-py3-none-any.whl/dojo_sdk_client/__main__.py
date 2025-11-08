import argparse
import asyncio
import logging
import os

# from .agents.anthropic_cua import AnthropicCUA
from .agents.example_agent import ExampleAgent
from .dojo_eval_client import DojoEvalClient
from .utils import load_tasks_from_hf_dataset

API_KEY = os.getenv("DOJO_API_KEY")
# agent = AnthropicCUA(model="claude-4-sonnet-20250514", image_context_length=4, verbose=False)
agent = ExampleAgent()

logger = logging.getLogger(__name__)


async def main():
    """Main entry point for the dojo package."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)s - %(message)s",
    )

    parser = argparse.ArgumentParser(description="Dojo Client - Run AI agent evaluations")
    parser.add_argument(
        "--hf-dataset", type=str, help="HuggingFace dataset name to load tasks from (e.g., 'chakra-labs/dojo-bench-mini')"
    )
    parser.add_argument("--tasks", nargs="*", help="Specific tasks to run (e.g., 'action-tester/must-click')")

    args = parser.parse_args()

    if args.hf_dataset:
        print(f"Loading tasks from HuggingFace dataset: {args.hf_dataset}")
        await run_hf_dataset_tasks(args.hf_dataset, args.tasks)
    else:
        print("Evaluating by dojos")
        await by_task_name(args.tasks)


async def run_hf_dataset_tasks(dataset_name: str, specific_tasks: list[str] = None):
    """Run tasks from HuggingFace dataset."""
    client = DojoEvalClient(agent, API_KEY, verbose=True)

    if specific_tasks:
        # Use the specific tasks provided
        task_names = specific_tasks
        logger.info(f"Running {len(task_names)} specific tasks from HF dataset")
    else:
        # Load all tasks from the dataset
        task_names = load_tasks_from_hf_dataset(dataset_name)
        logger.info(f"Running all {len(task_names)} tasks from HF dataset")

    logger.info("Tasks to run:")
    for task_name in task_names:
        logger.info(f"  - {task_name}")

    await client.evaluate(tasks=task_names, num_runners=1)


async def by_task_name(specific_tasks: list[str] = None):
    """Run tasks using the traditional dojo loader."""
    client = DojoEvalClient(agent, API_KEY, verbose=True)

    if specific_tasks:
        task_names = specific_tasks
    else:
        # Default tasks for backward compatibility
        task_names = ["action-tester/must-click", "tic-tac-toe/lose-game"]

    logger.info(f"Running {len(task_names)} tasks using traditional dojo loader")

    await client.evaluate(tasks=task_names, num_runners=1)


if __name__ == "__main__":
    asyncio.run(main())
