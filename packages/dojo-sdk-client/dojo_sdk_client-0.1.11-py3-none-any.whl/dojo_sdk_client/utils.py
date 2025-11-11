import logging

from dojo_sdk_core.tasks import RemoteTaskLoader

logger = logging.getLogger(__name__)


def load_tasks_from_hf_dataset(dataset_name: str) -> list[str]:
    """Load all tasks from HuggingFace dataset and return as dojo_name/task_id format."""
    loader = RemoteTaskLoader(dataset_name)
    all_tasks = loader._get_all_tasks()

    task_list = []
    for task in all_tasks:
        # Extract dojo name from environment path (e.g., "spas/2048/app" -> "2048")
        env_path = task.environment.path
        if env_path and "spas/" in env_path:
            # Extract dojo name from path like "spas/2048/app" or "spas/action-tester/app/dist/index.html"
            path_parts = env_path.split("/")
            if len(path_parts) >= 2 and path_parts[0] == "spas":
                dojo_name = path_parts[1]
        elif env_path and "index.html" in env_path:
            # Extract dojo name from path like ".../2048/index.html"
            path_parts = env_path.split("/")
            if len(path_parts) >= 2 and path_parts[-1] == "index.html":
                dojo_name = path_parts[-2]

        if not dojo_name:
            raise ValueError(f"Dojo name not found for task {task.id} in environment path {env_path}")

        task_path = f"{dojo_name}/{task.id}"
        task_list.append(task_path)

    logger.info(f"Loaded {len(task_list)} tasks from HF dataset {dataset_name}")
    return task_list
