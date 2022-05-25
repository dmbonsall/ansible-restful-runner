from unittest.mock import patch
from unittest.mock import MagicMock

from restful_runner.utils import status_handler, build_status_handler


def _assert_status_handler_updates_fields(database_mock, status, field_list):
    status_dict = {"runner_ident": "abcd", "status": status}
    status_handler(None, status_dict, MagicMock())
    database_mock.update_ansible_job.assert_called_once()

    for field in field_list:
        assert field in database_mock.update_ansible_job.call_args.kwargs


@patch("restful_runner.utils.database")
def test_status_handler_starting(database_mock):
    _assert_status_handler_updates_fields(
        database_mock, "starting", ["status", "start_time"]
    )


@patch("restful_runner.utils.database")
def test_status_handler_running(database_mock):
    _assert_status_handler_updates_fields(database_mock, "running", ["status"])


@patch("restful_runner.utils.database")
def test_status_handler_other(database_mock):
    fields = ["status", "end_time"]
    _assert_status_handler_updates_fields(database_mock, "successful", fields)
    database_mock.reset_mock()
    _assert_status_handler_updates_fields(database_mock, "timeout", fields)
    database_mock.reset_mock()
    _assert_status_handler_updates_fields(database_mock, "failed", fields)
    database_mock.reset_mock()
    _assert_status_handler_updates_fields(database_mock, "canceled", fields)


@patch("restful_runner.utils.status_handler")
def test_build_status_handler(status_handler_mock):
    sessionmaker_mock = MagicMock()
    session_mock = sessionmaker_mock.return_value
    session_mock.__enter__.return_value = session_mock
    wrapper = build_status_handler(sessionmaker_mock)
    assert callable(wrapper)
    wrapper(None, None)
    status_handler_mock.assert_called_once_with(session_mock, None, None)
