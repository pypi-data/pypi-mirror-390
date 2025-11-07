from __future__ import annotations

import asyncio
import time
from types import TracebackType
from typing import (
    Any,
    AsyncGenerator,
    AsyncIterator,
    Callable,
    Dict,
    Iterator,
    Literal,
    Mapping,
    MutableMapping,
    Optional,
    Sequence,
    TypedDict,
    cast,
)

import httpx

from .exceptions import TaskForceAIError

DEFAULT_BASE_URL = "https://taskforceai.chat/api/developer"
JsonDict = Dict[str, Any]
Headers = Mapping[str, str]


class TaskSubmissionResponse(TypedDict, total=False):
    taskId: str
    status: Literal["processing", "completed", "failed"]
    message: str
    warnings: Sequence[str]
    metadata: Dict[str, Any]


class TaskStatusPayload(TypedDict, total=False):
    taskId: str
    status: Literal["processing", "completed", "failed"]
    result: Any
    error: str
    warnings: Sequence[str]
    metadata: Dict[str, Any]


TaskSubmissionOptions = Mapping[str, Any]
ResponseHook = Callable[[httpx.Response], None]
TaskStatusCallback = Callable[[TaskStatusPayload], None]


def _merge_options(
    base_options: Optional[TaskSubmissionOptions],
    *,
    silent: Optional[bool],
    mock: Optional[bool],
) -> Dict[str, Any]:
    options: Dict[str, Any] = {"silent": False, "mock": False}
    if base_options:
        options.update(dict(base_options))
    if silent is not None:
        options["silent"] = silent
    if mock is not None:
        options["mock"] = mock
    return options


class TaskStatusStream(Iterator[TaskStatusPayload]):
    def __init__(
        self,
        client: "TaskForceAIClient",
        task_id: str,
        *,
        poll_interval: float,
        max_attempts: int,
        on_status: Optional[TaskStatusCallback] = None,
    ) -> None:
        self._client = client
        self._task_id = task_id
        self._poll_interval = poll_interval
        self._max_attempts = max_attempts
        self._on_status = on_status
        self._cancelled = False
        self._iterator = self._generator()
        self.task_id = task_id

    def cancel(self) -> None:
        self._cancelled = True

    def __iter__(self) -> "TaskStatusStream":
        return self

    def __next__(self) -> TaskStatusPayload:
        return next(self._iterator)

    def _generator(self) -> Iterator[TaskStatusPayload]:
        attempts = 0
        while attempts < self._max_attempts:
            if self._cancelled:
                raise TaskForceAIError("Task stream cancelled")

            status = self._client.get_task_status(self._task_id)
            if self._on_status:
                self._on_status(status)

            yield status

            state = status.get("status")
            if state in {"completed", "failed"}:
                return

            attempts += 1
            time.sleep(self._poll_interval)

        raise TaskForceAIError("Task did not complete within the expected time")


class AsyncTaskStatusStream(AsyncIterator[TaskStatusPayload]):
    def __init__(
        self,
        client: "AsyncTaskForceAIClient",
        task_id: str,
        *,
        poll_interval: float,
        max_attempts: int,
        on_status: Optional[TaskStatusCallback] = None,
    ) -> None:
        self._client = client
        self._task_id = task_id
        self._poll_interval = poll_interval
        self._max_attempts = max_attempts
        self._on_status = on_status
        self._cancelled = False
        self._iterator = self._generator()
        self.task_id = task_id

    def cancel(self) -> None:
        self._cancelled = True

    def __aiter__(self) -> "AsyncTaskStatusStream":
        return self

    async def __anext__(self) -> TaskStatusPayload:
        return await self._iterator.__anext__()

    async def _generator(self) -> AsyncGenerator[TaskStatusPayload, None]:
        attempts = 0
        while attempts < self._max_attempts:
            if self._cancelled:
                raise TaskForceAIError("Task stream cancelled")

            status = await self._client.get_task_status(self._task_id)
            if self._on_status:
                self._on_status(status)

            yield status

            state = status.get("status")
            if state in {"completed", "failed"}:
                return

            attempts += 1
            await asyncio.sleep(self._poll_interval)

        raise TaskForceAIError("Task did not complete within the expected time")


def _extract_error_message(response: httpx.Response) -> str:
    try:
        data = response.json()
        if isinstance(data, dict):
            error_payload = cast(Dict[str, Any], data)
            error_value = error_payload.get("error")
            if isinstance(error_value, str):
                return error_value
            if error_value is not None:
                return str(error_value)
    except ValueError:
        pass

    text = response.text
    return text or f"HTTP {response.status_code}"


class TaskForceAIClient:
    """Synchronous TaskForceAI client."""

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 30.0,
        transport: Optional[httpx.BaseTransport] = None,
        response_hook: Optional[ResponseHook] = None,
    ) -> None:
        if not api_key.strip():
            raise TaskForceAIError("API key must be a non-empty string")

        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._client = httpx.Client(timeout=timeout, transport=transport)
        self._response_hook = response_hook

    def __enter__(self) -> "TaskForceAIClient":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.close()

    def close(self) -> None:
        self._client.close()

    def _headers(self) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            "x-api-key": self._api_key,
        }

    def _request(
        self,
        method: str,
        endpoint: str,
        json: Optional[JsonDict] = None,
    ) -> JsonDict:
        url = f"{self._base_url}{endpoint}"
        try:
            response = self._client.request(
                method=method,
                url=url,
                json=json,
                headers=self._headers(),
                timeout=self._timeout,
            )
            if self._response_hook:
                self._response_hook(response)
            response.raise_for_status()
            return cast(JsonDict, response.json())
        except httpx.TimeoutException as exc:
            raise TaskForceAIError("Request timeout") from exc
        except httpx.HTTPStatusError as exc:
            message = _extract_error_message(exc.response)
            raise TaskForceAIError(message, status_code=exc.response.status_code) from exc
        except httpx.HTTPError as exc:
            raise TaskForceAIError(f"Network error: {exc}") from exc

    def submit_task(
        self,
        prompt: str,
        *,
        options: Optional[TaskSubmissionOptions] = None,
        silent: Optional[bool] = None,
        mock: Optional[bool] = None,
        open_router_key: Optional[str] = None,
    ) -> str:
        if not prompt.strip():
            raise TaskForceAIError("Prompt must be a non-empty string")

        payload: JsonDict = {"prompt": prompt, "options": _merge_options(options, silent=silent, mock=mock)}
        if open_router_key:
            payload["openRouterKey"] = open_router_key

        data = cast(TaskSubmissionResponse, self._request("POST", "/run", json=payload))
        task_id = data.get("taskId")
        if not isinstance(task_id, str):
            raise TaskForceAIError("API did not return a taskId")
        return task_id

    def get_task_status(self, task_id: str) -> TaskStatusPayload:
        if not task_id.strip():
            raise TaskForceAIError("Task ID must be a non-empty string")
        return cast(TaskStatusPayload, self._request("GET", f"/status/{task_id}"))

    def get_task_result(self, task_id: str) -> TaskStatusPayload:
        if not task_id.strip():
            raise TaskForceAIError("Task ID must be a non-empty string")
        return cast(TaskStatusPayload, self._request("GET", f"/results/{task_id}"))

    def wait_for_completion(
        self,
        task_id: str,
        *,
        poll_interval: float = 2.0,
        max_attempts: int = 150,
        on_status: Optional[TaskStatusCallback] = None,
    ) -> TaskStatusPayload:
        for _ in range(max_attempts):
            status = self.get_task_status(task_id)
            state = status.get("status")

            if on_status:
                on_status(status)

            if state == "completed" and "result" in status:
                status.setdefault("taskId", task_id)
                return status

            if state == "failed":
                detail = status.get("error") or "Task failed"
                raise TaskForceAIError(detail)

            time.sleep(poll_interval)

        raise TaskForceAIError("Task did not complete within the expected time")

    def run_task(
        self,
        prompt: str,
        *,
        options: Optional[TaskSubmissionOptions] = None,
        silent: Optional[bool] = None,
        mock: Optional[bool] = None,
        open_router_key: Optional[str] = None,
        poll_interval: float = 2.0,
        max_attempts: int = 150,
        on_status: Optional[TaskStatusCallback] = None,
    ) -> TaskStatusPayload:
        task_id = self.submit_task(
            prompt,
            options=options,
            silent=silent,
            mock=mock,
            open_router_key=open_router_key,
        )
        return self.wait_for_completion(
            task_id,
            poll_interval=poll_interval,
            max_attempts=max_attempts,
            on_status=on_status,
        )

    def stream_task_status(
        self,
        task_id: str,
        *,
        poll_interval: float = 2.0,
        max_attempts: int = 150,
        on_status: Optional[TaskStatusCallback] = None,
    ) -> TaskStatusStream:
        if not task_id.strip():
            raise TaskForceAIError("Task ID must be a non-empty string")
        return TaskStatusStream(
            self,
            task_id,
            poll_interval=poll_interval,
            max_attempts=max_attempts,
            on_status=on_status,
        )

    def run_task_stream(
        self,
        prompt: str,
        *,
        options: Optional[TaskSubmissionOptions] = None,
        silent: Optional[bool] = None,
        mock: Optional[bool] = None,
        open_router_key: Optional[str] = None,
        poll_interval: float = 2.0,
        max_attempts: int = 150,
        on_status: Optional[TaskStatusCallback] = None,
    ) -> TaskStatusStream:
        task_id = self.submit_task(
            prompt,
            options=options,
            silent=silent,
            mock=mock,
            open_router_key=open_router_key,
        )
        return TaskStatusStream(
            self,
            task_id,
            poll_interval=poll_interval,
            max_attempts=max_attempts,
            on_status=on_status,
        )


class AsyncTaskForceAIClient:
    """Asynchronous TaskForceAI client."""

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 30.0,
        transport: Optional[httpx.AsyncBaseTransport] = None,
        response_hook: Optional[ResponseHook] = None,
    ) -> None:
        if not api_key.strip():
            raise TaskForceAIError("API key must be a non-empty string")

        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._client = httpx.AsyncClient(timeout=timeout, transport=transport)
        self._response_hook = response_hook

    async def __aenter__(self) -> "AsyncTaskForceAIClient":
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self.close()

    async def close(self) -> None:
        await self._client.aclose()

    def _headers(self) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            "x-api-key": self._api_key,
        }

    async def _request(
        self,
        method: str,
        endpoint: str,
        json: Optional[JsonDict] = None,
    ) -> JsonDict:
        url = f"{self._base_url}{endpoint}"
        try:
            response = await self._client.request(
                method=method,
                url=url,
                json=json,
                headers=self._headers(),
                timeout=self._timeout,
            )
            if self._response_hook:
                self._response_hook(response)
            response.raise_for_status()
            return cast(JsonDict, response.json())
        except httpx.TimeoutException as exc:
            raise TaskForceAIError("Request timeout") from exc
        except httpx.HTTPStatusError as exc:
            message = _extract_error_message(exc.response)
            raise TaskForceAIError(message, status_code=exc.response.status_code) from exc
        except httpx.HTTPError as exc:
            raise TaskForceAIError(f"Network error: {exc}") from exc

    async def submit_task(
        self,
        prompt: str,
        *,
        options: Optional[TaskSubmissionOptions] = None,
        silent: Optional[bool] = None,
        mock: Optional[bool] = None,
        open_router_key: Optional[str] = None,
    ) -> str:
        if not prompt.strip():
            raise TaskForceAIError("Prompt must be a non-empty string")

        payload: JsonDict = {"prompt": prompt, "options": _merge_options(options, silent=silent, mock=mock)}
        if open_router_key:
            payload["openRouterKey"] = open_router_key

        data = cast(TaskSubmissionResponse, await self._request("POST", "/run", json=payload))
        task_id = data.get("taskId")
        if not isinstance(task_id, str):
            raise TaskForceAIError("API did not return a taskId")
        return task_id

    async def get_task_status(self, task_id: str) -> TaskStatusPayload:
        if not task_id.strip():
            raise TaskForceAIError("Task ID must be a non-empty string")
        return cast(TaskStatusPayload, await self._request("GET", f"/status/{task_id}"))

    async def get_task_result(self, task_id: str) -> TaskStatusPayload:
        if not task_id.strip():
            raise TaskForceAIError("Task ID must be a non-empty string")
        return cast(TaskStatusPayload, await self._request("GET", f"/results/{task_id}"))

    async def wait_for_completion(
        self,
        task_id: str,
        *,
        poll_interval: float = 2.0,
        max_attempts: int = 150,
        on_status: Optional[TaskStatusCallback] = None,
    ) -> TaskStatusPayload:
        for _ in range(max_attempts):
            status = await self.get_task_status(task_id)
            state = status.get("status")

            if on_status:
                on_status(status)

            if state == "completed" and "result" in status:
                status.setdefault("taskId", task_id)
                return status

            if state == "failed":
                detail = status.get("error") or "Task failed"
                raise TaskForceAIError(detail)

            await asyncio.sleep(poll_interval)

        raise TaskForceAIError("Task did not complete within the expected time")

    async def run_task(
        self,
        prompt: str,
        *,
        options: Optional[TaskSubmissionOptions] = None,
        silent: Optional[bool] = None,
        mock: Optional[bool] = None,
        open_router_key: Optional[str] = None,
        poll_interval: float = 2.0,
        max_attempts: int = 150,
        on_status: Optional[TaskStatusCallback] = None,
    ) -> TaskStatusPayload:
        task_id = await self.submit_task(
            prompt,
            options=options,
            silent=silent,
            mock=mock,
            open_router_key=open_router_key,
        )
        return await self.wait_for_completion(
            task_id,
            poll_interval=poll_interval,
            max_attempts=max_attempts,
            on_status=on_status,
        )

    def stream_task_status(
        self,
        task_id: str,
        *,
        poll_interval: float = 2.0,
        max_attempts: int = 150,
        on_status: Optional[TaskStatusCallback] = None,
    ) -> AsyncTaskStatusStream:
        if not task_id.strip():
            raise TaskForceAIError("Task ID must be a non-empty string")
        return AsyncTaskStatusStream(
            self,
            task_id,
            poll_interval=poll_interval,
            max_attempts=max_attempts,
            on_status=on_status,
        )

    async def run_task_stream(
        self,
        prompt: str,
        *,
        options: Optional[TaskSubmissionOptions] = None,
        silent: Optional[bool] = None,
        mock: Optional[bool] = None,
        open_router_key: Optional[str] = None,
        poll_interval: float = 2.0,
        max_attempts: int = 150,
        on_status: Optional[TaskStatusCallback] = None,
    ) -> AsyncTaskStatusStream:
        task_id = await self.submit_task(
            prompt,
            options=options,
            silent=silent,
            mock=mock,
            open_router_key=open_router_key,
        )
        return AsyncTaskStatusStream(
            self,
            task_id,
            poll_interval=poll_interval,
            max_attempts=max_attempts,
            on_status=on_status,
        )
