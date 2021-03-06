import pytest
from balsa import Balsa

from longtaskrunnin import application_name, author


@pytest.fixture(scope="session", autouse=True)
def long_task_runnin_session():
    balsa = balsa_factory()
    balsa.init_logger()


def balsa_factory() -> Balsa:
    balsa = Balsa(application_name, author, delete_existing_log_files=True, log_directory="log", verbose=True, gui=True)
    return balsa
