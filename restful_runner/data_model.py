from sqlalchemy import Column, DateTime, Enum, Integer, JSON, String
from sqlalchemy.orm import declarative_base

from restful_runner import schema

Base = declarative_base()


class AnsibleJob(Base):  # type: ignore[valid-type,misc]
    __tablename__ = "ansible_jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_uuid = Column(String, unique=True)
    job_name = Column(String)
    initiator = Column(String)
    status = Column(Enum(schema.AnsibleRunnerStatus), nullable=True)
    start_time = Column(DateTime)
    end_time = Column(DateTime, nullable=True)
    result = Column(JSON, nullable=True)
