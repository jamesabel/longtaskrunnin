import threading

from PyQt5.QtCore import Qt

from longtaskrunnin import LongTaskRunnin

start_threads = threading.enumerate()


def tst(qtbot):
    long_task_runnin = LongTaskRunnin()
    qtbot.addWidget(long_task_runnin)
    with qtbot.waitExposed(long_task_runnin):
        for _ in range(0, 4):
            qtbot.mouseClick(long_task_runnin.do_something_interactive_button, Qt.LeftButton, delay=1 * 1000)
        qtbot.mouseClick(long_task_runnin.quit_button, Qt.LeftButton, delay=1 * 1000)
        qtbot.waitUntil(long_task_runnin.long_task_runnin_is_closed, timeout=60 * 1000)

    # in various situations, such as running pytest in PyCharm as "debug", PyQt's QThreads can leak threads even after the application has closed.
    for thread in threading.enumerate():
        if thread not in start_threads:
            print(f"leaking thread : {thread.name=}")


# run multiple times to see if we get a thread leak


def test_longtaskrunnin_1(qtbot):
    tst(qtbot)


def test_longtaskrunnin_2(qtbot):
    tst(qtbot)


def test_longtaskrunnin_3(qtbot):
    tst(qtbot)
