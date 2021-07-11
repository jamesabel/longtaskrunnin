from PyQt5.QtCore import Qt

from longtaskrunnin import LongTaskRunnin


def test_longtaskrunnin(qtbot):
    long_task_runnin = LongTaskRunnin()
    qtbot.addWidget(long_task_runnin)
    qtbot.wait_for_window_shown(long_task_runnin)
    for _ in range(0, 4):
        qtbot.mouseClick(long_task_runnin.do_something_interactive_button, Qt.LeftButton, delay=1 * 1000)
    qtbot.mouseClick(long_task_runnin.quit_button, Qt.LeftButton, delay=1 * 1000)
    qtbot.waitUntil(long_task_runnin.dft_is_closed, timeout=60 * 1000)
