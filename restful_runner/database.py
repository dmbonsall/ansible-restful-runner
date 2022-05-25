from typing import List

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session

from restful_runner.data_model import AnsibleJob
from restful_runner.schema import AnsibleRunnerStatus


class DatabaseConnection:
    def __init__(self, db_url: str) -> None:
        self._engine = create_engine(db_url, connect_args={"check_same_thread": False})

        self._session_local = sessionmaker(
            autocommit=False, autoflush=False, bind=self._engine
        )

    def get_engine(self) -> Engine:
        return self._engine

    def session_local(self) -> Session:
        return self._session_local()


def create_ansible_job(
    session: Session, job_uuid: str, job_name: str, initiator: str
) -> AnsibleJob:
    ansible_job = AnsibleJob(
        job_uuid=job_uuid,
        job_name=job_name,
        initiator=initiator,
        status=AnsibleRunnerStatus.CREATED,
    )
    session.add(ansible_job)
    session.commit()
    session.refresh(ansible_job)
    return ansible_job


def get_ansible_job(session: Session, job_uuid: str) -> AnsibleJob:
    return session.query(AnsibleJob).filter(AnsibleJob.job_uuid == job_uuid).one()


def get_ansible_jobs(
    session: Session, skip: int = 0, limit: int = 100
) -> List[AnsibleJob]:
    return (
        session.query(AnsibleJob)
        .order_by(AnsibleJob.start_time.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def update_ansible_job(session: Session, job_uuid: str, **kwargs) -> None:
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
        updated_rows = (
            session.query(AnsibleJob)
            .filter(AnsibleJob.job_uuid == job_uuid)
            .update(update_dict)
        )

        if updated_rows == 0:
            raise IndexError(f"No job with UUID: {job_uuid}")
        if updated_rows > 1:
            session.rollback()
            raise RuntimeError(
                f"More than one row ({updated_rows} rows) have UUID: {job_uuid}"
            )

        session.commit()


def delete_ansible_job(session: Session, job_uuid: str) -> None:
    updated_rows = (
        session.query(AnsibleJob).filter(AnsibleJob.job_uuid == job_uuid).delete()
    )

    if updated_rows == 0:
        raise IndexError(f"No job with UUID: {job_uuid}")
    if updated_rows > 1:
        session.rollback()
        raise RuntimeError(
            f"More than one row ({updated_rows} rows) have UUID: {job_uuid}"
        )

    session.commit()
