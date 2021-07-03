import time
from multiprocessing import Process
import shelve
from pathlib import Path
from dataclasses import dataclass
from enum import Enum, auto

import appdirs
from PyQt5.Qt import pyqtSignal, QThread
from PyQt5.QtWidgets import QMainWindow, QFrame, QVBoxLayout, QLineEdit, QLabel, QPushButton

from longtaskrunnin import application_name, author


class ReturnTechnique(Enum):
    use_pyqtsignal = auto()
    use_shelve = auto()


# change these to run the various experiments
use_qthread = True
use_process = True
force_error = False
return_technique = ReturnTechnique.use_shelve


def options_str() -> str:
    return f"{use_qthread=},{use_process=},{force_error=},{return_technique=}"


@dataclass
class EInfo:
    e_value: float = 0.0
    duration: float = 0.0
    iterations: int = 1


def get_shelf_file_path() -> str:
    d = Path(appdirs.user_data_dir(application_name, author))
    d.mkdir(parents=True, exist_ok=True)
    return str(Path(d, application_name))


class LongTaskWorkerProcess(Process):

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

        if force_error:
            div_error_value = 1.0/0.0

        k = 1.0
        while time.time() - start_time < self.requested_duration:
            self.e_info.e_value += 1.0 / k
            k *= self.e_info.iterations
            self.e_info.iterations += 1
            self.e_info.duration = time.time() - start_time

        if return_technique.use_shelve:
            # "write back" the result via a shelf
            with shelve.open(get_shelf_file_path()) as shelf:
                shelf["e"] = self.e_info

        # on exit of this method, the result is in self.e_info


class LongTaskWorkerThread(QThread):

    def __init__(self, long_task_signal):
        self.long_task_signal = long_task_signal
        super().__init__()

    def run(self):
        long_task_worker_process = LongTaskWorkerProcess()
        if use_process:
            long_task_worker_process.start()
            long_task_worker_process.join()
        else:
            long_task_worker_process.run()  # use LongTaskWorkerProcess() as a function (will block)
        self.long_task_signal.emit()  # tell main thread to update its display


class LongTaskRunnin(QMainWindow):
    long_task_signal = pyqtSignal()

    def __init__(self):
        super().__init__()

        # set up the visual elements
        self.frame = QFrame()
        self.setWindowTitle(application_name)
        self.setCentralWidget(self.frame)
        layout = QVBoxLayout()
        self.duration_display = QLineEdit("")
        self.e_display = QLineEdit()
        self.iterations_display = QLineEdit()
        self.ok_button = QPushButton("Click if ran OK")
        self.ok_button.clicked.connect(self.ran_ok)
        self.ran_ok_flag = False
        self.ran_ok_count = 0
        layout.addWidget(QLabel(f"{use_qthread=}"))
        layout.addWidget(QLabel(f"{use_process=}"))
        layout.addWidget(QLabel(f"{force_error=}"))
        layout.addWidget(QLabel(f"{return_technique=}"))
        layout.addWidget(self.duration_display)
        layout.addWidget(self.e_display)
        layout.addWidget(self.iterations_display)
        layout.addWidget(self.ok_button)
        self.frame.setLayout(layout)
        self.show()

        # QThread (which may use Process)
        if return_technique.use_shelve:
            self.long_task_signal.connect(self.display_e_via_shelve)
        else:
            self.long_task_signal.connect(self.display_e_info)
        self.long_task_worker_thread = LongTaskWorkerThread(self.long_task_signal)
        self.long_task_worker_thread.start()

    def display_e_via_shelve(self):
        try:
            with shelve.open(get_shelf_file_path()) as shelf:
                if (e_info := shelf.get("e")) is not None:
                    self.display_e_info(e_info)
                shelf.close()
        except (FileNotFoundError, PermissionError):
            # can happen when shelf is not initialized
            pass

    def display_e_info(self, e_info: EInfo):
        self.duration_display.setText(str(e_info.duration))
        self.e_display.setText(str(e_info.e_value))
        self.iterations_display.setText(str(e_info.iterations))

    def ran_ok(self):
        # do something to make sure the UI is working
        self.ran_ok_flag = True
        self.ok_button.setText(f"You said it ran OK! ({self.ran_ok_count=})")
        self.ran_ok_count += 1
