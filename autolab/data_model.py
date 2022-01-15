import enum

from sqlalchemy import Column, DateTime, Enum, Integer, JSON, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class AnsibleRunnerStatus(enum.Enum):
    CREATED = "created"
    STARTING = "starting"
    RUNNING = "running"
    SUCCESSFUL = "successful"
    TIMEOUT = "timeout"
    FAILED = "failed"
    CANCELED = "canceled"


class VmTemplateType(enum.Enum):
    ALMA = "AlmaCloudInit"
    UBUNTU = "UbuntuCloudInit"


class AnsibleJob(Base):
    __tablename__ = "ansible_jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_uuid = Column(String, unique=True)
    job_name = Column(String)
    initiator = Column(String)
    status = Column(Enum(AnsibleRunnerStatus), nullable=True)
    start_time = Column(DateTime)
    end_time = Column(DateTime, nullable=True)
    result = Column(JSON, nullable=True)
