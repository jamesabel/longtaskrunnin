import pytest
from pytestqt.qtbot import QtBot
from balsa import Balsa

from longtaskrunnin import application_name, author


@pytest.fixture(scope="session", autouse=True)
def long_task_runnin_session():
    balsa = Balsa(application_name, author, delete_existing_log_files=True, log_directory="log", verbose=False)
    balsa.init_logger()


@pytest.fixture
def qtbot(qapp, request):
    return QtBot(request)
