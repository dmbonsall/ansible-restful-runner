import datetime

import ansible_runner

from restful_runner import database
from restful_runner.schema import AnsibleRunnerStatus, StatusHandlerStatus


def status_handler(status: StatusHandlerStatus, runner_config: ansible_runner.RunnerConfig):
    """Callback to handle changes to status."""
    status = StatusHandlerStatus(**status)
    cur_time = datetime.datetime.now()
    if status.status == AnsibleRunnerStatus.STARTING:
        database.update_ansible_job(runner_config.ident, start_time=cur_time, status=status.status)
    elif status.status == AnsibleRunnerStatus.RUNNING:
        database.update_ansible_job(runner_config.ident, status=status.status)
    else:
        # We have reached a terminal state
        database.update_ansible_job(runner_config.ident, status=status.status, end_time=cur_time)
