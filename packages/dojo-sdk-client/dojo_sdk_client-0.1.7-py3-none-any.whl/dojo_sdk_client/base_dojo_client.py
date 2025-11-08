import logging
from io import BytesIO
from typing import Any, Optional

import aiohttp
import PIL.Image
import requests
from dojo_sdk_core.settings import settings
from dojo_sdk_core.ws_types import HistoryStep

from .telemetry.dojo_telemetry import telemetry
from .types import NoRunnersAvailableError, TaskResponse, TaskStatus

logger = logging.getLogger(__name__)


class BaseDojoClient:
    """Barebones HTTP client for Dojo"""

    def __init__(self, api_key: str) -> None:
        self.api_key: str = api_key
        self.http_endpoint: str = settings.dojo_http_endpoint
        self.tasks = set()

    def _get_headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.api_key}"}

    @telemetry.track("create_task")
    async def create_task(
        self,
        task_id: str,
        state: dict[str, Any],
        metadata: Optional[dict[str, str]] = None,
    ) -> dict[str, Any]:
        """Create a task execution"""
        async with aiohttp.request(
            "POST",
            f"{self.http_endpoint}/tasks",
            json={
                "task_id": task_id,
                "metadata": metadata or {},
                "state": state,
            },
            headers=self._get_headers(),
        ) as response:
            response.raise_for_status()
            resp = await response.json()
            exec_id = resp["exec_id"]
            return exec_id

    @telemetry.track_sync("create_task_sync")
    def create_task_sync(
        self,
        task_id: str,
        state: dict[str, Any],
        metadata: Optional[dict[str, str]] = None,
    ) -> dict[str, Any]:
        """Create a task execution"""
        response = requests.post(
            f"{self.http_endpoint}/tasks",
            json={
                "task_id": task_id,
                "metadata": metadata or {},
                "state": state,
            },
            headers=self._get_headers(),
        )
        response.raise_for_status()
        resp = response.json()
        return resp["exec_id"]

    @telemetry.track("start_task")
    async def start_task(self, exec_id: str):
        """Start a task execution"""
        async with aiohttp.request(
            "POST", f"{self.http_endpoint}/tasks/start", json={"exec_id": exec_id}, headers=self._get_headers()
        ) as response:
            if response.status == 200:
                return

            resp = await response.json()
            if resp.get("error") == "TASK_CAPACITY_REACHED":
                raise NoRunnersAvailableError()
            else:
                response.raise_for_status()

    @telemetry.track_sync("start_task_sync")
    def start_task_sync(self, exec_id: str):
        """Start a task execution"""
        response = requests.post(
            f"{self.http_endpoint}/tasks/start",
            json={"exec_id": exec_id},
            headers=self._get_headers(),
        )
        response.raise_for_status()
        return

    @telemetry.track("get_task_status")
    async def get_task_status(self, exec_id: str) -> TaskResponse:
        """Get task status at a specific step"""
        async with aiohttp.request(
            "GET", f"{self.http_endpoint}/tasks/{exec_id}/status", headers=self._get_headers()
        ) as response:
            response.raise_for_status()
            result = await response.json()
            history = result.get("history", [])
            if history is None:
                history = []
            return TaskResponse(
                status=TaskStatus(result.get("status")),
                screenshot=result.get("screenshot"),
                history=[HistoryStep(**h) for h in history],
                step=result.get("step"),
                state=result.get("state"),
                error_detail=result.get("error_detail"),
            )

    @telemetry.track_sync("get_task_status_sync")
    def get_task_status_sync(self, exec_id: str) -> TaskResponse:
        """Get task status at a specific step"""
        response = requests.get(f"{self.http_endpoint}/tasks/{exec_id}/status", headers=self._get_headers())
        response.raise_for_status()
        result = response.json()
        history = result.get("history", [])
        if history is None:
            history = []
        return TaskResponse(
            status=TaskStatus(result.get("status")),
            screenshot=result.get("screenshot"),
            history=[HistoryStep(**h) for h in history],
            step=result.get("step"),
            state=result.get("state"),
            error_detail=result.get("error_detail"),
        )

    @telemetry.track("submit_action")
    async def submit_action(
        self,
        exec_id: str,
        action: dict[str, Any],
        agent_response: str = "No thoughts provided",
        raw_response: str = "Not provided",
    ) -> dict[str, Any]:
        """Submit an action for a task"""
        async with aiohttp.request(
            "POST",
            f"{self.http_endpoint}/tasks/actions",
            json={
                "action": action,
                "agent_response": agent_response,
                "exec_id": exec_id,
                "raw_response": raw_response,
            },
            headers=self._get_headers(),
        ) as response:
            response.raise_for_status()
            return await response.json()

    @telemetry.track_sync("submit_action_sync")
    def submit_action_sync(
        self,
        exec_id: str,
        action: dict[str, Any],
        agent_response: str = "No thoughts provided",
        raw_response: str = "Not provided",
    ) -> dict[str, Any]:
        """Submit an action for a task"""
        response = requests.post(
            f"{self.http_endpoint}/tasks/actions",
            json={
                "action": action,
                "agent_response": agent_response,
                "exec_id": exec_id,
                "raw_response": raw_response,
            },
            headers=self._get_headers(),
        )
        response.raise_for_status()
        return response.json()

    @telemetry.track("submit_step_score")
    async def submit_step_score(self, exec_id: str, step_number: int, score: float) -> dict[str, Any]:
        """Submit a step score for a task"""
        async with aiohttp.request(
            "POST",
            f"{self.http_endpoint}/tasks/{exec_id}/submit_step_score",
            json={"step_number": step_number, "score": score},
            headers=self._get_headers(),
        ) as response:
            response.raise_for_status()
            return await response.json()

    @telemetry.track_sync("submit_step_score_sync")
    def submit_step_score_sync(self, exec_id: str, step_number: int, score: float) -> dict[str, Any]:
        """Submit a step score for a task"""
        response = requests.post(
            f"{self.http_endpoint}/tasks/{exec_id}/submit_step_score",
            json={"step_number": step_number, "score": score},
            headers=self._get_headers(),
        )
        response.raise_for_status()
        return response.json()

    @telemetry.track("get_image")
    async def get_image(self, path: str) -> PIL.Image.Image:
        """Get an image from the server"""
        async with aiohttp.request("GET", f"{self.http_endpoint}/image?path={path}", headers=self._get_headers()) as response:
            response.raise_for_status()
            return PIL.Image.open(BytesIO(await response.read()))

    @telemetry.track_sync("get_image_sync")
    def get_image_sync(self, path: str) -> PIL.Image.Image:
        """Get an image from the server"""
        response = requests.get(f"{self.http_endpoint}/image?path={path}", headers=self._get_headers())
        response.raise_for_status()
        return PIL.Image.open(BytesIO(response.content))

    @telemetry.track("stop_task")
    async def stop_task(self, exec_id: str, status: TaskStatus = TaskStatus.COMPLETED) -> dict[str, Any]:
        """Stop a task execution"""
        async with aiohttp.request(
            "POST", f"{self.http_endpoint}/tasks/stop", json={"exec_id": exec_id, "status": status}, headers=self._get_headers()
        ) as response:
            response.raise_for_status()
            return await response.json()

    @telemetry.track_sync("stop_task_sync")
    def stop_task_sync(self, exec_id: str, status: TaskStatus = TaskStatus.COMPLETED) -> dict[str, Any]:
        """Stop a task execution synchronously"""
        response = requests.post(
            f"{self.http_endpoint}/tasks/stop",
            json={"exec_id": exec_id, "status": status},
            headers=self._get_headers(),
            timeout=5,
        )
        return response.json()
