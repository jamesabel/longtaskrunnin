import time
from multiprocessing import get_logger
import math
from typing import Dict, Any


from PyQt5.Qt import pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QFrame, QVBoxLayout, QLineEdit, QLabel, QPushButton

from longtaskrunnin import application_name, EInfo, LongTaskWorkerThread, use_process, force_error

time_start = time.time()

log = get_logger()


def options_str() -> str:
    return f"{use_process=},{force_error=}"


class LongTaskRunnin(QMainWindow):

    long_task_signal = pyqtSignal(EInfo)  # to update the display with the values from calculating "e"

    def __init__(self, log_config_as_dict: Dict[str, Any]):
        self.log_config_as_dict = log_config_as_dict
        super().__init__()

        self.e = None  # not yet calculated

        # set up the visual elements
        self.frame = QFrame()
        self.setWindowTitle(application_name)
        self.setCentralWidget(self.frame)
        layout = QVBoxLayout()
        self.duration_display = QLineEdit("")
        self.duration_display.setReadOnly(True)
        self.e_display = QLineEdit()
        self.e_display.setReadOnly(True)
        self.iterations_display = QLineEdit()
        self.iterations_display.setReadOnly(True)
        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.long_task_runnin_start)
        self.do_something_interactive_button = QPushButton("Click me")
        self.do_something_interactive_button.clicked.connect(self.interactive_button)
        self.do_something_interactive_button_count = 0
        self.quit_button = QPushButton("Quit")
        self.quit_button.clicked.connect(self.long_task_runnin_quit)
        layout.addWidget(QLabel(f"{use_process=}"))
        layout.addWidget(QLabel(f"{force_error=}"))
        layout.addWidget(self.duration_display)
        layout.addWidget(self.e_display)
        layout.addWidget(self.iterations_display)
        # layout.addWidget(self.interprocess_communications_file_path_display)
        layout.addWidget(self.start_button)
        layout.addWidget(self.do_something_interactive_button)
        layout.addWidget(self.quit_button)

        self.frame.setLayout(layout)
        self.show()

        self.long_task_worker_thread = None

        # when the worker is finished this will be "signaled" with the path of the file that contains the results (as a pickle file).
        self.long_task_signal.connect(self.display_e_info)

    def check_result(self):
        """
        Make sure we've actually done the work. Log an error if apparently never started, and throw an "assert" if the answer seemed to be computed but was wrong.
        """
        if self.e is None:
            log.error("Tried to check the result, but the calculation of e has not yet been run.")
        else:
            assert math.isclose(self.e, math.e, rel_tol=0.01)

    def display_e_info(self):
        """
        Display the "e" values once they've been calculated
        """
        e_info = self.long_task_worker_thread.return_value
        self.e = e_info.e_value
        self.duration_display.setText(str(e_info.duration))
        self.e_display.setText(str(e_info.e_value))
        self.iterations_display.setText(str(e_info.iterations))

    def long_task_runnin_start(self):
        # start doing the work
        if self.long_task_worker_thread is not None and self.long_task_worker_thread.isRunning():
            log.warning("already running")
        else:
            self.long_task_worker_thread = LongTaskWorkerThread(self.long_task_signal, self.log_config_as_dict)
            # self.interprocess_communications_file_path_display.setText(self.long_task_worker_thread.interprocess_communication.get_interprocess_communication_file_path_str())
            self.long_task_worker_thread.start()

    def interactive_button(self):
        # do something interactive to make sure the UI is working
        self.do_something_interactive_button.setText(f"I've been clicked! ({self.do_something_interactive_button_count=})")
        self.do_something_interactive_button_count += 1

    def long_task_runnin_quit(self):
        # quit the app
        if self.long_task_worker_thread is not None:
            # make sure the worker is done
            log.debug(f"{self.long_task_worker_thread.isRunning()=}")
            self.long_task_worker_thread.wait()
            log.debug(f"{self.long_task_worker_thread.isRunning()=}")
        self.check_result()
        self.close()

    def long_task_runnin_is_closed(self) -> bool:
        # for pytest-qt
        assert not self.isVisible()
        return True
