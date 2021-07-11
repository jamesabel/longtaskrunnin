from PyQt5.QtCore import Qt

from longtaskrunnin import LongTaskRunnin


def test_longtaskrunning(qtbot):
    long_task_runnin = LongTaskRunnin()
    qtbot.addWidget(long_task_runnin)
    qtbot.wait_for_window_shown(long_task_runnin)
    qtbot.mouseClick(long_task_runnin.quit_button, Qt.LeftButton, delay=3 * 1000)  # run norn
    qtbot.waitUntil(long_task_runnin.dft_norn_run_complete, timeout=60 * 1000)
