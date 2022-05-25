import datetime
from typing import Callable, Dict

import ansible_runner
from sqlalchemy.orm import Session

from restful_runner import database
from restful_runner.schema import (
    AnsibleRunnerStatus,
    StatusHandlerStatus,
    StatusHandlerInterface,
)


def status_handler(
    session: Session,
    status_dict: Dict[str, str],
    runner_config: ansible_runner.RunnerConfig,
) -> None:
    """Callback to handle changes to status."""
    status = StatusHandlerStatus(**status_dict)
    cur_time = datetime.datetime.now()
    if status.status == AnsibleRunnerStatus.STARTING:
        database.update_ansible_job(
            session, runner_config.ident, start_time=cur_time, status=status.status
        )
    elif status.status == AnsibleRunnerStatus.RUNNING:
        database.update_ansible_job(session, runner_config.ident, status=status.status)
    else:
        # We have reached a terminal state
        database.update_ansible_job(
            session, runner_config.ident, status=status.status, end_time=cur_time
        )


def build_status_handler(sessionmaker: Callable[[], Session]) -> StatusHandlerInterface:
    def wrapper(status: Dict[str, str], runner_config: ansible_runner.RunnerConfig):
        with sessionmaker() as session:
            status_handler(session, status, runner_config)

    return wrapper
