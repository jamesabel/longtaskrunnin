import time
from multiprocessing import Process
import shelve
from pathlib import Path
from dataclasses import dataclass
from enum import Enum, auto
from typing import Union

import appdirs
from PyQt5.Qt import pyqtSignal, QThread
from PyQt5.QtWidgets import QMainWindow, QFrame, QVBoxLayout, QLineEdit

from longtaskrunnin import application_name, author


class ReturnTechnique(Enum):
    use_pyqtsignal = auto()
    use_shelve = auto()


use_qthread = True
use_process = True
return_technique = ReturnTechnique.use_shelve


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

    def __init__(self, long_task_signal: Union[pyqtSignal, None] = None, requested_duration: float = 5.0):
        self.long_task_signal = long_task_signal
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
            self.e_info.e_value += 1.0 / k
            k *= self.e_info.iterations
            self.e_info.iterations += 1
            self.e_info.duration = time.time() - start_time

        if return_technique.use_shelve:
            # "write back" the result via a shelf
            with shelve.open(get_shelf_file_path()) as shelf:
                shelf["e"] = self.e_info
            if self.long_task_signal is not None:
                self.long_task_signal.emit()  # merely signal "done"
        else:
            self.long_task_signal.emit(self.e_info)  # pass result back via the signal


class LongTaskWorkerThread(QThread):

    def __init__(self, long_task_signal):
        self.long_task_signal = long_task_signal
        super().__init__()

    def run(self):
        waste_some_time = LongTaskWorkerProcess()
        waste_some_time.start()
        waste_some_time.join()
        self.long_task_signal.emit()  # tell main thread to update its display


class LongTaskRunnin(QMainWindow):
    long_task_signal = pyqtSignal()

    def __init__(self):
        super().__init__()

        # set up the visual elements
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

        if use_qthread:
            if use_process:
                # QThread and Process
                self.long_task_signal.connect(self.display_e)
                self.long_task_worker_thread = LongTaskWorkerThread(self.long_task_signal)
                self.long_task_worker_thread.start()
            else:
                # QThread only
                pass
        elif use_process:
            # Process only
            self.long_task_worker_process = LongTaskWorkerProcess(self.long_task_signal)
            self.long_task_worker_process.start()
        else:
            # neither QThread nor Process - nothing to do
            assert RuntimeError(f"{use_qthread=},{use_process}")

    def display_e(self):
        if return_technique.use_shelve:
            try:
                with shelve.open(get_shelf_file_path()) as shelf:
                    if (e_info := shelf.get("e")) is not None:
                        self.display_e_info(e_info)
                    shelf.close()
            except (FileNotFoundError, PermissionError):
                pass

    def display_e_info(self, e_info: EInfo):
        self.duration_display.setText(str(e_info.duration))
        self.e_display.setText(str(e_info.e_value))
        self.iterations_display.setText(str(e_info.iterations))
