import enum
import datetime
from typing import Any, Callable, Dict, List, Optional

import ansible_runner
from pydantic import BaseModel  # pylint: disable=no-name-in-module


class AnsibleRunnerStatus(enum.Enum):
    """Status of an ansible job."""

    CREATED = "created"
    STARTING = "starting"
    RUNNING = "running"
    SUCCESSFUL = "successful"
    TIMEOUT = "timeout"
    FAILED = "failed"
    CANCELED = "canceled"


class AnsibleJob(BaseModel):
    """Information about an ansible job."""

    job_uuid: str
    status: AnsibleRunnerStatus
    start_time: Optional[datetime.datetime]
    end_time: Optional[datetime.datetime] = None
    result: Optional[Any] = None

    class Config:
        orm_mode = True


class StatusHandlerStatus(BaseModel):
    """The status structure that is passed back from the ansible_runner.Runner class to status handler."""

    status: AnsibleRunnerStatus
    runner_ident: str


class StartPlaybookRequest(BaseModel):
    """Request model for starting a playbook."""

    extravars: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None


StatusHandlerInterface = Callable[
    [StatusHandlerStatus, ansible_runner.interface.RunnerConfig], None
]
