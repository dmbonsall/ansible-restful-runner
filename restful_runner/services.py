from concurrent.futures import Executor, Future
import logging
from typing import Any, Dict, List, Optional

import ansible_runner
import ansible_runner.interface


from restful_runner import config
from restful_runner.schema import StatusHandlerInterface


logger = logging.getLogger("restful_runner")


class PlaybookExecutorService:
    def __init__(self, executor: Executor, status_handler: StatusHandlerInterface):
        self._executor: Executor = executor
        self._status_handler = status_handler
        self._future_map = {}

    def submit_job(self, ident: str, playbook: str, extravars: Optional[Dict[str, Any]] = None,
                   tags: Optional[List[str]] = None):
        if extravars is None:
            extravars = {}

        cmdline = f"--tags {','.join(tags)}" if tags else ""

        settings = config.get_app_settings()
        future = self._executor.submit(ansible_runner.run,
                                       status_handler = self._status_handler,
                                       quiet=settings.ansible_quiet,
                                       project_dir=settings.project_dir,
                                       artifact_dir=settings.artifact_dir,
                                       private_data_dir=settings.private_data_dir,
                                       ident=ident,
                                       playbook=playbook,
                                       extravars=extravars,
                                       cmdline=cmdline,)

        future.add_done_callback(self.done_callback)
        self._future_map[ident] = future
        logger.info("Submitted job: %s", ident)

    def done_callback(self, future: Future):
        runner: ansible_runner.Runner = future.result()
        self._future_map.pop(runner.config.ident)
        logger.info("Finished job: %s", runner.config.ident)
