from dataclasses import dataclass
from typing import Callable, Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session

from restful_runner.data_model import AnsibleJob
from restful_runner.schema import AnsibleRunnerStatus


class DatabaseNotInitializedError(RuntimeError):
    pass


def _null_sessionmaker() -> Session:
    raise DatabaseNotInitializedError()


@dataclass
class _DatabaseState:
    session_local: Callable = _null_sessionmaker
    engine: Optional[Engine] = None


_db_state = _DatabaseState()


def initialize(db_url):
    if _db_state.engine is None:
        _db_state.engine = create_engine(
            db_url, connect_args={"check_same_thread": False}
        )

        _db_state.session_local = sessionmaker(autocommit=False, autoflush=False, bind=_db_state.engine)
    else:
        raise RuntimeWarning("Database already initialized.")

def get_engine():
    if _db_state.engine is None:
        raise DatabaseNotInitializedError()

    return _db_state.engine


def create_ansible_job(job_uuid: str, job_name: str, initiator: str):
    with _db_state.session_local() as session:
        ansible_job = AnsibleJob(job_uuid=job_uuid, job_name=job_name, initiator=initiator,
                                 status=AnsibleRunnerStatus.CREATED)
        session.add(ansible_job)
        session.commit()
        session.refresh(ansible_job)
        return ansible_job


def get_ansible_job(job_uuid: str):
    with _db_state.session_local() as session:
        return session.query(AnsibleJob).filter(AnsibleJob.job_uuid == job_uuid).one()


def get_ansible_jobs(skip: int = 0, limit: int = 100):
    with _db_state.session_local() as session:
        return session.query(AnsibleJob).order_by(AnsibleJob.start_time.desc()).offset(skip).limit(limit).all()


def update_ansible_job(job_uuid: str, **kwargs):
    update_dict = {}
    if "status" in kwargs:
        update_dict[AnsibleJob.status] = kwargs["status"]

    if "start_time" in kwargs:
        update_dict[AnsibleJob.start_time] = kwargs["start_time"]

    if "end_time" in kwargs:
        update_dict[AnsibleJob.end_time] = kwargs["end_time"]

    if "result" in kwargs:
        update_dict[AnsibleJob.result] = kwargs["result"]

    if update_dict:
        with _db_state.session_local() as session:
            updated_rows = session.query(AnsibleJob) \
                            .filter(AnsibleJob.job_uuid == job_uuid) \
                            .update(update_dict)

            if updated_rows == 0:
                raise IndexError(f"No job with UUID: {job_uuid}")
            if updated_rows > 1:
                session.rollback()
                raise RuntimeError(f"More than one row ({updated_rows} rows) have UUID: {job_uuid}")

            session.commit()


def delete_ansible_job(job_uuid:str):
    with _db_state.session_local() as session:
        updated_rows = session.query(AnsibleJob) \
                              .filter(AnsibleJob.job_uuid == job_uuid) \
                              .delete()

        if updated_rows == 0:
            raise IndexError(f"No job with UUID: {job_uuid}")
        if updated_rows > 1:
            session.rollback()
            raise RuntimeError(f"More than one row ({updated_rows} rows) have UUID: {job_uuid}")

        session.commit()
