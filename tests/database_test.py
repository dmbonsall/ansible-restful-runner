import datetime
from unittest.mock import MagicMock

import pytest
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from restful_runner import database
from restful_runner.database import DatabaseConnection
from restful_runner.data_model import AnsibleJob


def test_database_connection():
    """Tests all functionality of the DatabaseConnection class."""
    db_conn = DatabaseConnection("sqlite://")  # In memory

    assert isinstance(db_conn.get_engine(), Engine)
    with db_conn.session_local() as sess:
        assert isinstance(sess, Session)


def test_create_ansible_job():
    """Tests creating an ansible job."""
    session_mock = MagicMock()
    ansible_job = database.create_ansible_job(
        session_mock, "abcd", "test-job", "test-initiator"
    )

    session_mock.add.assert_called_once_with(ansible_job)
    session_mock.commit.assert_called_once()
    session_mock.refresh.asssert_called_once_with(ansible_job)
    assert isinstance(ansible_job, AnsibleJob)


def test_get_ansible_job():
    """Tests getting a single ansible job."""
    session_mock = MagicMock()
    database.get_ansible_job(session_mock, "abcd")
    session_mock.query.assert_called_once_with(AnsibleJob)


def test_get_ansible_jobs():
    """Tests getting multiple ansible jobs."""
    session_mock = MagicMock()
    database.get_ansible_jobs(session_mock)
    session_mock.query.assert_called_once_with(AnsibleJob)


def test_update_ansible_job_no_operation():
    """Tests updating an ansible job without providing attributes to update."""
    session_mock = MagicMock()
    database.update_ansible_job(session_mock, "abcd")
    session_mock.query.assert_not_called()
    session_mock.commit.assert_not_called()
    session_mock.rollback.assert_not_called()


def test_update_ansible_job_all_params():
    """Tests updating all updateable attributes on an ansible job."""
    session_mock = MagicMock()
    filter_mock = session_mock.query.return_value
    update_mock = filter_mock.filter.return_value
    update_mock.update.return_value = 1

    database.update_ansible_job(
        session_mock,
        "abcd",
        status="test-status",
        start_time=datetime.datetime(2022, 1, 1, 0, 0, 0),
        end_time=datetime.datetime(2022, 1, 1, 0, 0, 10),
        result="test-result",
    )

    session_mock.query.assert_called_once_with(AnsibleJob)
    filter_mock.filter.assert_called_once()
    update_mock.update.assert_called_once()
    assert len(update_mock.update.call_args.args[0]) == 4
    session_mock.commit.assert_called_once()
    session_mock.rollback.assert_not_called()


def test_update_ansible_job_one_param():
    """Tests updating a single attribute on an ansible job."""
    session_mock = MagicMock()
    filter_mock = session_mock.query.return_value
    update_mock = filter_mock.filter.return_value
    update_mock.update.return_value = 1

    database.update_ansible_job(
        session_mock,
        "abcd",
        status="test-status",
    )

    session_mock.query.assert_called_once_with(AnsibleJob)
    filter_mock.filter.assert_called_once()
    update_mock.update.assert_called_once()
    assert len(update_mock.update.call_args.args[0]) == 1
    session_mock.commit.assert_called_once()
    session_mock.rollback.assert_not_called()


def test_update_ansible_job_does_not_exist():
    """Tests updating an ansible job that does not exist."""
    session_mock = MagicMock()
    session_mock.query.return_value.filter.return_value.update.return_value = 0

    with pytest.raises(IndexError):
        database.update_ansible_job(
            session_mock,
            "abcd",
            status="test-status",
        )

    session_mock.commit.assert_not_called()
    session_mock.rollback.assert_not_called()


def test_update_ansible_job_multiple_keys():
    """Tests updating an ansible job when db contains multiple job for uuid."""
    session_mock = MagicMock()
    session_mock.query.return_value.filter.return_value.update.return_value = 2

    with pytest.raises(RuntimeError):
        database.update_ansible_job(
            session_mock,
            "abcd",
            status="test-status",
        )

    session_mock.commit.assert_not_called()
    session_mock.rollback.assert_called_once()


def test_delete_ansible_job():
    """Tests deleting an ansible job in the database."""
    session_mock = MagicMock()
    session_mock.query.return_value.filter.return_value.delete.return_value = 1
    database.delete_ansible_job(session_mock, "abcd")
    session_mock.query.return_value.filter.return_value.delete.assert_called_once()
    session_mock.commit.assert_called_once()
    session_mock.rollback.assert_not_called()


def test_delete_ansible_job_does_not_exist():
    """Tests deleting an ansible job that does not exist."""
    session_mock = MagicMock()
    session_mock.query.return_value.filter.return_value.delete.return_value = 0
    with pytest.raises(IndexError):
        database.delete_ansible_job(session_mock, "abcd")
    session_mock.commit.assert_not_called()
    session_mock.rollback.assert_not_called()


def test_delete_ansible_job_multiple_keys():
    """Tests deleting an ansible job when db contains multiple job for uuid."""
    session_mock = MagicMock()
    session_mock.query.return_value.filter.return_value.delete.return_value = 2
    with pytest.raises(RuntimeError):
        database.delete_ansible_job(session_mock, "abcd")
    session_mock.commit.assert_not_called()
    session_mock.rollback.assert_called_once()
