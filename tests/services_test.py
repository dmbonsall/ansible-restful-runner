from unittest import TestCase
from unittest.mock import MagicMock
from unittest.mock import ANY

import ansible_runner

from restful_runner.services import PlaybookExecutorService
from restful_runner.config import ApplicationSettings


class PlaybookExecutorServiceTestCase(TestCase):
    def setUp(self) -> None:
        self.executor_mock = MagicMock()
        self.status_handler_mock = MagicMock()
        self.settings = ApplicationSettings()

        self.service = PlaybookExecutorService(
            self.executor_mock, self.status_handler_mock, self.settings
        )

    def assert_executor_submit_called_once_with(
        self, ident, playbook, extravars, cmdline
    ):
        self.executor_mock.submit.assert_called_once_with(
            ansible_runner.run,
            status_handler=self.status_handler_mock,
            quiet=ANY,
            project_dir=ANY,
            artifact_dir=ANY,
            private_data_dir=ANY,
            ident=ident,
            playbook=playbook,
            extravars=extravars,
            cmdline=cmdline,
        )

    def test_submit_job(self):
        """Tests the typical submit job invocation cases."""
        self.service.submit_job("abcdef", "playbook.yml")

        self.assert_executor_submit_called_once_with(
            ident="abcdef", playbook="playbook.yml", extravars={}, cmdline=""
        )
        assert len(self.service._future_map) == 1

    def test_submit_job_with_extravars(self):
        """Tests the submit job with extravars."""
        extravars = {"var1": "val1", "var2": "val2"}
        self.service.submit_job("abcdef", "playbook.yml", extravars=extravars)

        self.assert_executor_submit_called_once_with(
            ident="abcdef", playbook="playbook.yml", extravars=extravars, cmdline=""
        )
        assert len(self.service._future_map) == 1

    def test_submit_job_with_tags(self):
        """Tests the submit job with extravars."""
        tags = ["tag1", "tag2"]
        self.service.submit_job("abcdef", "playbook.yml", tags=tags)

        self.assert_executor_submit_called_once_with(
            ident="abcdef",
            playbook="playbook.yml",
            extravars={},
            cmdline="--tags tag1,tag2",
        )
        assert len(self.service._future_map) == 1

    def test_done_callback(self):
        future_mock = MagicMock()
        runner_mock = future_mock.result.return_value
        runner_mock.config.ident = "abcd"

        self.service._future_map["abcd"] = None
        self.service.done_callback(future_mock)
        assert len(self.service._future_map) == 0
