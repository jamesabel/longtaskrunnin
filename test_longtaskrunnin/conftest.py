import pytest
from pytestqt.qtbot import QtBot

@pytest.fixture
def qtbot(qapp, request):
    return QtBot(request)
