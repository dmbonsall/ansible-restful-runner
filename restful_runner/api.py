from concurrent.futures import ThreadPoolExecutor
import os
import os.path
from typing import List
import uuid

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session

from restful_runner import database, config, data_model, services, utils
from restful_runner.schema import AnsibleJob, StartPlaybookRequest


# ===== Get the settings and initialize everything =====
settings = config.get_app_settings()

db = database.DatabaseConnection(settings.db_url)
data_model.Base.metadata.create_all(bind=db.get_engine())


def get_session():
    session = db.session_local()
    try:
        yield session
    finally:
        session.close()


executor = ThreadPoolExecutor(max_workers=settings.max_executor_threads)
executor_service = services.PlaybookExecutorService(executor, utils.status_handler)


app = FastAPI()


@app.get("/")
def get_root():
    return "OK"


@app.get("/playbooks", response_model=List[str])
def get_playbooks():
    if settings.project_dir is None:
        project_dir = os.path.join(settings.private_data_dir, "project")
    else:
        project_dir = settings.project_dir

    filenames = os.listdir(project_dir)
    playbooks = [
        name for name in filenames if os.path.splitext(name)[1] in (".yml", ".yaml")
    ]
    return playbooks


@app.post("/playbooks/{playbook}", response_model=AnsibleJob)
def start_playbook(
    playbook: str,
    request_data: StartPlaybookRequest,
    session: Session = Depends(get_session),
):
    ident = str(uuid.uuid1())
    database.create_ansible_job(session, ident, playbook, "REST")
    executor_service.submit_job(
        ident, playbook, request_data.extravars, request_data.tags
    )
    return database.get_ansible_job(session, ident)


@app.get("/jobs", response_model=List[AnsibleJob])
def get_jobs(
    session: Session = Depends(get_session),
):
    return database.get_ansible_jobs(session)


@app.get("/jobs/{job_uuid}", response_model=AnsibleJob)
def get_job_by_uuid(
    job_uuid: str,
    session: Session = Depends(get_session),
):
    job = database.get_ansible_job(session, job_uuid)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
