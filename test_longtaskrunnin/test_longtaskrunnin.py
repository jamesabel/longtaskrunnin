import threading
import time

from PyQt5.QtCore import Qt
from balsa import get_logger

from longtaskrunnin import LongTaskRunnin, application_name

start_threads = threading.enumerate()


log = get_logger(application_name)


def print_leaking_threads() -> bool:
    # PyQt's QThreads can leak "Dummy" threads even after the PyQt application has closed
    any_leaking_threads = False
    for thread in threading.enumerate():
        if thread not in start_threads:
            log.warning(f"leaking thread : {thread.name=}")
            any_leaking_threads = True
    return any_leaking_threads


def tst(qtbot):
    long_task_runnin = LongTaskRunnin()
    qtbot.addWidget(long_task_runnin)
    with qtbot.waitExposed(long_task_runnin):
        start_time = time.time()
        qtbot.mouseClick(long_task_runnin.start_button, Qt.LeftButton)  # start the run
        log.debug(f"after start click {time.time() - start_time} seconds")
        for _ in range(0, 6):
            time.sleep(1.0)  # mouseClick(delay) seems to take processing resources ... ?
            log.debug(f"before interactive click {time.time() - start_time} seconds")
            qtbot.mouseClick(long_task_runnin.do_something_interactive_button, Qt.LeftButton)  # some GUI interactivity
        log.debug(f"before quit click {time.time() - start_time} seconds")
        qtbot.mouseClick(long_task_runnin.quit_button, Qt.LeftButton, delay=3 * 1000)  # quit GUI
        log.debug(f"before waitUntil {time.time() - start_time} seconds")
        qtbot.waitUntil(long_task_runnin.long_task_runnin_is_closed, timeout=60 * 1000)  # wait for GUI to close
        log.debug(f"after waitUntil {time.time() - start_time} seconds")

    print_leaking_threads()


# run multiple times to see if we get a thread leak


def test_longtaskrunnin_1(qtbot):
    tst(qtbot)


def test_longtaskrunnin_2(qtbot):
    tst(qtbot)


def test_longtaskrunnin_3(qtbot):
    tst(qtbot)


def test_longtaskrunnin_4(qtbot):
    tst(qtbot)


def test_longtaskrunnin_5(qtbot):
    tst(qtbot)
