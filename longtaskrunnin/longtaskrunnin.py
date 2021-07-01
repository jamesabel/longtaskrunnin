import time
from multiprocessing import Process
import shelve
from pathlib import Path
from dataclasses import dataclass

import appdirs
from PyQt5.Qt import pyqtSignal, QThread
from PyQt5.QtWidgets import QMainWindow, QFrame, QVBoxLayout, QLineEdit

from longtaskrunnin import application_name, author


@dataclass
class EInfo:
    e: float = 0.0
    duration: float = 0.0
    iterations: int = 1


def get_shelf_file_path() -> str:
    d = Path(appdirs.user_data_dir(application_name, author))
    d.mkdir(parents=True, exist_ok=True)
    return str(Path(d, application_name))


class WasteSomeTime(Process):

    def __init__(self, requested_duration: float = 5.0):
        self.requested_duration = requested_duration
        self.e_info = EInfo()
        super().__init__()

    def run(self):
        """
        Waste some time by calculating the "e" by iteration. Return an object that is relatively arbitrary in contents and size
        (as opposed to, say, a float).
        """
        start_time = time.time()
        k = 1.0
        while time.time() - start_time < self.requested_duration:
            self.e_info.e += 1.0/k
            k *= self.e_info.iterations
            self.e_info.iterations += 1
            self.e_info.duration = time.time() - start_time

        # "write back" the result via a shelf
        with shelve.open(get_shelf_file_path()) as shelf:
            shelf["e"] = self.e_info


class LongTaskWorkerThread(QThread):

    def __init__(self, long_task_signal):
        self.long_task_signal = long_task_signal
        super().__init__()

    def run(self):
        waste_some_time = WasteSomeTime()
        waste_some_time.start()
        waste_some_time.join()
        self.long_task_signal.emit()  # tell main thread to update its display


class LongTaskRunnin(QMainWindow):
    long_task_signal = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.frame = QFrame()
        self.setCentralWidget(self.frame)
        layout = QVBoxLayout()
        self.duration_display = QLineEdit("")
        self.e_display = QLineEdit()
        self.iterations_display = QLineEdit()
        layout.addWidget(self.duration_display)
        layout.addWidget(self.e_display)
        layout.addWidget(self.iterations_display)
        self.frame.setLayout(layout)
        self.show()

        self.long_task_signal.connect(self.display_e)
        self.long_task_worker_thread = LongTaskWorkerThread(self.long_task_signal)
        self.long_task_worker_thread.start()

    def display_e(self):
        try:
            with shelve.open(get_shelf_file_path()) as shelf:
                e = shelf.get("e", EInfo())

                self.duration_display.setText(str(e.duration))
                self.e_display.setText(str(e.e))
                self.iterations_display.setText(str(e.iterations))

                shelf.close()
        except (FileNotFoundError, PermissionError):
            pass
