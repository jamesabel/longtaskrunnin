from PyQt5.QtCore import Qt

from longtaskrunnin import LongTaskRunnin


def tst(qtbot):
    long_task_runnin = LongTaskRunnin()
    qtbot.addWidget(long_task_runnin)
    with qtbot.waitExposed(long_task_runnin):
        for _ in range(0, 4):
            qtbot.mouseClick(long_task_runnin.do_something_interactive_button, Qt.LeftButton, delay=1 * 1000)
        qtbot.mouseClick(long_task_runnin.quit_button, Qt.LeftButton, delay=1 * 1000)
        qtbot.waitUntil(long_task_runnin.long_task_runnin_is_closed, timeout=60 * 1000)


def test_longtaskrunnin_1(qtbot):
    tst(qtbot)


def test_longtaskrunnin_2(qtbot):
    tst(qtbot)
