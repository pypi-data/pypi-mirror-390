"""
Module containing the Event Worker used for executing flow runs directly in the worker process.

To start a Event Worker, run the following command:

```bash
prefect worker start --pool 'my-work-pool' --type event-process
```
"""

from __future__ import annotations

import asyncio
import contextlib
import os
import tempfile
import threading
import uuid
from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Optional, TypeVar

import anyio
import anyio.abc
import diskcache
from pydantic import Field, field_validator

from prefect._internal.schemas.validators import validate_working_dir
from prefect.client.schemas.objects import Flow as APIFlow
from prefect.events import Event
from prefect.events.clients import PrefectEventSubscriber
from prefect.events.filters import EventFilter, EventNameFilter
from prefect.exceptions import MissingFlowError
from prefect.flow_engine import run_flow
from prefect.flows import load_flow_from_entrypoint, load_function_and_convert_to_flow
from prefect.runner.runner import Runner
from prefect.settings import PREFECT_WORKER_QUERY_SECONDS
from prefect.states import Pending
from prefect.utilities.processutils import get_sys_executable
from prefect.utilities.services import (
    critical_service_loop,
    start_client_metrics_server,
    stop_client_metrics_server,
)
from prefect.workers.base import (
    BaseJobConfiguration,
    BaseVariables,
    BaseWorker,
    BaseWorkerResult,
)

if TYPE_CHECKING:
    from prefect.client.schemas.objects import FlowRun, WorkPool
    from prefect.client.schemas.responses import DeploymentResponse
    from prefect.flows import Flow

FR = TypeVar("FR")  # used to capture the return type of a flow


class EventProcessJobConfiguration(BaseJobConfiguration):
    stream_output: bool = Field(default=True)
    working_dir: Optional[Path] = Field(default=None)

    @field_validator("working_dir")
    @classmethod
    def validate_working_dir(cls, v: Path | str | None) -> Path | None:
        if isinstance(v, str):
            return validate_working_dir(v)
        return v

    def prepare_for_flow_run(
        self,
        flow_run: "FlowRun",
        deployment: "DeploymentResponse | None" = None,
        flow: "APIFlow | None" = None,
        work_pool: "WorkPool | None" = None,
        worker_name: str | None = None,
    ) -> None:
        super().prepare_for_flow_run(flow_run, deployment, flow, work_pool, worker_name)

        self.env: dict[str, str | None] = {**os.environ, **self.env}
        self.command: str | None = (
            f"{get_sys_executable()} -m prefect.engine"
            if self.command == self._base_flow_run_command()
            else self.command
        )

    @staticmethod
    def _base_flow_run_command() -> str:
        """
        Override the base flow run command because enhanced cancellation doesn't
        work with the process worker.
        """
        return "python -m prefect.engine"


class EventProcessVariables(BaseVariables):
    stream_output: bool = Field(
        default=True,
        description=(
            "If enabled, workers will stream output from flow runs to "
            "local standard output."
        ),
    )
    working_dir: Optional[Path] = Field(
        default=None,
        title="Working Directory",
        description=(
            "If provided, workers will execute flows within the "
            "specified path as the working directory."
        ),
    )


class EventProcessWorkerResult(BaseWorkerResult):
    """Contains information about the final state of a completed flow execution"""


class EventProcessWorker(
    BaseWorker[
        EventProcessJobConfiguration, EventProcessVariables, EventProcessWorkerResult
    ]
):
    type = "event_process"
    job_configuration: type[EventProcessJobConfiguration] = EventProcessJobConfiguration
    job_configuration_variables: type[EventProcessVariables] | None = (
        EventProcessVariables
    )

    _description = (
        "Execute flow runs directly in the worker process for high performance. "
        "Ideal for local execution and event-driven workflows."
    )
    _display_name = "Event Process"
    _documentation_url = "https://docs.prefect.io/latest/get-started/quickstart"
    _logo_url = "https://cdn.sanity.io/images/3ugk85nk/production/356e6766a91baf20e1d08bbe16e8b5aaef4d8643-48x48.png"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Persistent event deduplication using diskcache
        cache_dir = Path.home() / ".prefect" / "event-deduplication"
        cache_dir.mkdir(parents=True, exist_ok=True)
        self._event_cache = diskcache.Cache(str(cache_dir))

    async def start(
        self,
        run_once: bool = False,
        with_healthcheck: bool = False,
        printer: Callable[..., None] = print,
    ) -> None:
        """
        Starts the worker and runs the main worker loops.

        By default, the worker will run loops to poll for scheduled/cancelled flow
        runs and sync with the Prefect API server.

        If `run_once` is set, the worker will only run each loop once and then return.

        If `with_healthcheck` is set, the worker will start a healthcheck server which
        can be used to determine if the worker is still polling for flow runs and restart
        the worker if necessary.

        Args:
            run_once: If set, the worker will only run each loop once then return.
            with_healthcheck: If set, the worker will start a healthcheck server.
            printer: A `print`-like function where logs will be reported.
        """
        healthcheck_server = None
        healthcheck_thread = None
        try:
            async with self as worker:
                # wait for an initial heartbeat to configure the worker
                await worker.sync_with_backend()
                # schedule the scheduled flow run polling loop
                async with anyio.create_task_group() as loops_task_group:
                    # schedule the sync loop
                    loops_task_group.start_soon(
                        partial(
                            critical_service_loop,
                            workload=self.sync_with_backend,
                            interval=self.heartbeat_interval_seconds,
                            run_once=run_once,
                            jitter_range=0.3,
                            backoff=4,
                        )
                    )

                    loops_task_group.start_soon(
                        self._subscribe_to_flow_run_events,
                    )

                    self._started_event = await self._emit_worker_started_event()

                    start_client_metrics_server()

                    if with_healthcheck:
                        from prefect.workers.server import build_healthcheck_server

                        # we'll start the ASGI server in a separate thread so that
                        # uvicorn does not block the main thread
                        healthcheck_server = build_healthcheck_server(
                            worker=worker,
                            query_interval_seconds=PREFECT_WORKER_QUERY_SECONDS.value(),
                        )
                        healthcheck_thread = threading.Thread(
                            name="healthcheck-server-thread",
                            target=healthcheck_server.run,
                            daemon=True,
                        )
                        healthcheck_thread.start()

                    printer(f"Worker {worker.name!r} started!")

                # If running once, wait for active runs to complete before exiting
                if run_once and self._limiter:
                    while self.limiter.borrowed_tokens > 0:
                        self._logger.debug(
                            "Waiting for %s active run(s) to finish before shutdown...",
                            self.limiter.borrowed_tokens,
                        )
                        await anyio.sleep(0.1)
        finally:
            stop_client_metrics_server()

            if healthcheck_server and healthcheck_thread:
                self._logger.debug("Stopping healthcheck server...")
                healthcheck_server.should_exit = True
                healthcheck_thread.join()
                self._logger.debug("Healthcheck server stopped.")

        printer(f"Worker {worker.name!r} stopped!")

    async def run(
        self,
        flow_run: "FlowRun",
        configuration: EventProcessJobConfiguration,
        task_status: Optional[anyio.abc.TaskStatus[int]] = None,
    ) -> EventProcessWorkerResult:
        if task_status is None:
            task_status = anyio.TASK_STATUS_IGNORED

        working_dir_ctx = (
            tempfile.TemporaryDirectory(suffix="prefect")
            if not configuration.working_dir
            else contextlib.nullcontext(configuration.working_dir)
        )
        with working_dir_ctx as working_dir:
            process = await self._runner.execute_flow_run(
                flow_run_id=flow_run.id,
                command=configuration.command,
                cwd=working_dir,
                env=configuration.env,
                stream_output=configuration.stream_output,
                task_status=task_status,
            )

        status_code = (
            getattr(process, "returncode", None)
            if getattr(process, "returncode", None) is not None
            else getattr(process, "exitcode", None)
        )

        if process is None or status_code is None:
            raise RuntimeError("Failed to start flow run process.")

        return EventProcessWorkerResult(
            status_code=status_code, identifier=str(process.pid)
        )

    async def _submit_adhoc_run(
        self,
        flow: "Flow[..., FR]",
        parameters: dict[str, Any] | None = None,
        job_variables: dict[str, Any] | None = None,
        task_status: anyio.abc.TaskStatus["FlowRun"] | None = None,
    ):
        flow_run = await self.client.create_flow_run(
            flow,
            parameters=parameters,
            state=Pending(),
            job_variables=job_variables,
            work_pool_name=self.work_pool.name,
            work_queue_name="".join(self._work_queues),
        )
        if task_status is not None:
            # Emit the flow run object to .submit to allow it to return a future as soon as possible
            task_status.started(flow_run)

        logger = self.get_flow_run_logger(flow_run)
        logger.debug("Executing flow directly in current process...")

        return await self._execute_flow_directly(
            flow=flow,
            flow_run=flow_run,
            parameters=parameters,
        )

    async def _execute_flow_directly(
        self,
        flow: "Flow[..., FR]",
        flow_run: "FlowRun",
        parameters: dict[str, Any] | None = None,
    ) -> None:
        logger = self.get_flow_run_logger(flow_run)
        logger.debug("Executing flow directly in current process...")

        asyncio.create_task(self._run_flow_async(flow, flow_run, parameters))

        logger.debug("Flow execution task created, running concurrently")

    async def _run_flow_async(
        self,
        flow: "Flow[..., FR]",
        flow_run: "FlowRun",
        parameters: dict[str, Any] | None = None,
    ) -> None:
        logger = self.get_flow_run_logger(flow_run)

        try:
            maybe_coro = run_flow(
                flow=flow,
                flow_run=flow_run,
                parameters=parameters,
            )

            if asyncio.iscoroutine(maybe_coro):
                await maybe_coro
            else:
                pass

        except Exception as e:
            logger.exception("Error executing flow in background task")
            await self._propose_crashed_state(flow_run, f"Flow execution failed: {e}")
        finally:
            logger.debug("Background flow execution complete")

    def _is_event_processed(self, event_id: str) -> bool:
        """Check if an event has already been processed using diskcache"""
        return event_id in self._event_cache

    def _mark_event_processed_atomically(self, event_id: str) -> bool:
        """
        Atomically mark an event as processed using diskcache.

        Returns:
            True if the event was successfully marked (first time processing),
            False if the event was already marked (duplicate).
        """
        # add() is atomic: only sets the key if it doesn't exist
        # Returns True if key was added, False if key already exists
        return self._event_cache.add(event_id, True)

    async def _process_event(self, event: Event) -> None:
        """Process a single event with error handling, concurrency limiting, and deduplication"""
        event_id = str(event.id)

        # Atomically check and mark event as processed in a single operation
        # This prevents race conditions when multiple tasks process the same event
        if not self._mark_event_processed_atomically(event_id):
            self._logger.debug(f"Skipping duplicate event: {event_id}")
            return

        try:
            # Acquire a token from the limiter to control concurrency
            if self._limiter:
                async with self._limiter:
                    await self._process_event_internal(event)
            else:
                await self._process_event_internal(event)

        except Exception as e:
            self._logger.error(
                f"Failed to process event {event.resource.id}: {e}", exc_info=True
            )

    async def _subscribe_to_flow_run_events(self) -> None:
        filter = EventFilter(
            event=EventNameFilter(
                prefix=[
                    f"{self._work_pool_name}.{'.'.join(self._work_queues)}.run.deployment"
                ]
            ),
        )

        retry_delays = [1, 2, 5, 10, 30, 60]  # 重连延迟序列（秒）
        retry_count = 0

        while True:
            try:
                self._logger.info("正在连接到事件流...")
                async with PrefectEventSubscriber(filter=filter) as subscriber:
                    self._logger.info("已成功连接到事件流")
                    retry_count = 0  # 重置重试计数

                    async with anyio.create_task_group() as events_task_group:
                        async for event in subscriber:
                            self._logger.info(f"Received event: {event}")

                            # 将事件处理任务添加到持久化的 task group
                            events_task_group.start_soon(self._process_event, event)

                # 如果正常退出，退出循环
                self._logger.info("事件流已正常关闭")

                break

            except asyncio.CancelledError:
                # Worker 正在关闭，不重试
                self._logger.info("事件订阅被取消，正在关闭...")
                break

            except TimeoutError as e:
                # WebSocket 连接或重连超时（PrefectEventSubscriber 不处理此异常）
                retry_count += 1
                delay = retry_delays[min(retry_count - 1, len(retry_delays) - 1)]
                self._logger.warning(
                    "事件流连接超时（尝试 #%d）: %s。将在 %d 秒后重试...",
                    retry_count,
                    str(e),
                    delay,
                )
                await asyncio.sleep(delay)

            except Exception as e:
                retry_count += 1
                delay = retry_delays[min(retry_count - 1, len(retry_delays) - 1)]
                self._logger.error(f"订阅事件流时发生意外错误: {e}")
                await asyncio.sleep(delay)

    async def _process_event_internal(self, event) -> None:
        """Internal event processing logic"""
        deployment_id = uuid.UUID(event.resource.id.replace("deployment.", ""))
        parameters = event.payload.get("parameters", {})
        job_variables = event.payload.get("job_variables", {})

        deployment = await self.client.read_deployment(deployment_id)
        flow = await self._load_flow(deployment)

        await self.submit(flow, parameters=parameters, job_variables=job_variables)

    async def _load_flow(self, deployment: "DeploymentResponse") -> "Flow":
        if deployment.entrypoint:
            # we should not accept a placeholder flow at runtime
            try:
                flow = load_flow_from_entrypoint(
                    deployment.entrypoint, use_placeholder_flow=False
                )
            except MissingFlowError:
                flow = load_function_and_convert_to_flow(deployment.entrypoint)
        else:
            raise ValueError(f"Deployment {deployment.id} does not have an entrypoint")

        return flow

    async def __aenter__(self) -> EventProcessWorker:
        await super().__aenter__()
        self._runner = await self._exit_stack.enter_async_context(
            Runner(pause_on_shutdown=False, limit=None)
        )
        return self

    async def __aexit__(self, *exc_info: Any) -> None:
        await super().__aexit__(*exc_info)
