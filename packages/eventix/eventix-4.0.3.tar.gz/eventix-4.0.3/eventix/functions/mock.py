import dataclasses
from contextlib import contextmanager
from unittest.mock import MagicMock

from lsrestclient import LsRestClient


def mock_eventix_task_scheduler(mocker, return_value=None):
    mock_object = mocker.patch("eventix.functions.task_scheduler.TaskScheduler.task_post", return_value=return_value)
    return mock_object
