from concurrent.futures import Executor, Future
import logging
from typing import Any, Dict, List, Optional

import ansible_runner
import ansible_runner.interface

from restful_runner.schema import StatusHandlerInterface
from restful_runner.config import ApplicationSettings
from restful_runner.config import get_app_settings


logger = logging.getLogger("restful_runner")


class PlaybookExecutorService:
    def __init__(
        self,
        executor: Executor,
        status_handler: StatusHandlerInterface,
        settings: Optional[ApplicationSettings] = None,
    ) -> None:
        self._executor: Executor = executor
        self._status_handler = status_handler
        self._settings = settings if settings is not None else get_app_settings()
        self._future_map: Dict[str, Future] = {}

    def submit_job(
        self,
        ident: str,
        playbook: str,
        extravars: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
    ) -> None:
        if extravars is None:
            extravars = {}

        cmdline = f"--tags {','.join(tags)}" if tags else ""

        future = self._executor.submit(
            ansible_runner.run,
            status_handler=self._status_handler,
            quiet=self._settings.ansible_quiet,
            project_dir=self._settings.project_dir,
            artifact_dir=self._settings.artifact_dir,
            private_data_dir=self._settings.private_data_dir,
            ident=ident,
            playbook=playbook,
            extravars=extravars,
            cmdline=cmdline,
        )

        future.add_done_callback(self.done_callback)
        self._future_map[ident] = future
        logger.info("Submitted job: %s", ident)

    def done_callback(self, future: Future) -> None:
        runner: ansible_runner.Runner = future.result()
        self._future_map.pop(runner.config.ident)
        logger.info("Finished job: %s", runner.config.ident)
