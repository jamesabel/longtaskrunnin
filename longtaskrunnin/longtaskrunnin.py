import time
import uuid
from multiprocessing import Process
import math


from PyQt5.Qt import pyqtSignal, QThread
from PyQt5.QtWidgets import QMainWindow, QFrame, QVBoxLayout, QLineEdit, QLabel, QPushButton
from balsa import Balsa, get_logger

from longtaskrunnin import application_name, author, EInfo, InterprocessCommunication, interprocess_communication_read


# change these to run the various experiments
use_process = True
force_error = False

time_start = time.time()

log = get_logger(application_name)


def options_str() -> str:
    return f"{use_process=},{force_error=}"


class LongTaskWorkerProcess(Process):
    """
    Run the worker as a Process. This also enabled parallelism (that running as a thread would not).
    """

    def __init__(self, interprocess_communication: InterprocessCommunication, requested_duration: float = 3.0):
        self._interprocess_communication = interprocess_communication
        self._requested_duration = requested_duration
        super().__init__()

    def run(self):
        """
        Waste some time by calculating the "e" by iteration. Return an object that is relatively arbitrary in contents and size
        (as opposed to, say, a float).
        """
        run_start_time = time.time()
        e_info = EInfo()
        e_info.uuid = str(uuid.uuid4())

        if force_error:
            div_error_value = 1.0 / 0.0

        # calculate "e"
        k = 1.0
        while time.time() - run_start_time < self._requested_duration:
            e_info.e_value += 1.0 / k
            k *= e_info.iterations + 1
            e_info.iterations += 1
        e_info.duration = time.time() - run_start_time
        self._interprocess_communication.write(e_info)

        # Log the run time. Process needs its own logger instance.
        logging_application_name = f"{application_name}_{self._interprocess_communication.interprocess_communication_directory.name}"
        balsa = Balsa(logging_application_name, author, log_directory="log", verbose=False, is_root=False)
        balsa.init_logger()
        _log = get_logger(logging_application_name)  # get logger first before doing the log since we calculate the run time in the log
        _log.info(f"LongTaskWorkerProcess.run() took {time.time() - run_start_time} seconds")


class LongTaskWorkerThread(QThread):
    """
    This thread connects the UI to the worker.
    """

    def __init__(self, long_task_signal: pyqtSignal):
        self._long_task_signal = long_task_signal
        self.interprocess_communication = InterprocessCommunication()
        super().__init__()

    def run(self):
        run_start_time = time.time()
        log.debug(f"LongTaskWorkerThread entering run()")

        long_task_worker_process = LongTaskWorkerProcess(self.interprocess_communication)
        if use_process:
            long_task_worker_process.start()
            long_task_worker_process.join()
        else:
            # Just use LongTaskWorkerProcess() as a (blocking) function. This works, but if there's an error this app just crashes with
            # a `Process finished with exit code -1073740791 (0xC0000409)` instead of a proper Python error message.
            long_task_worker_process.run()

        self._long_task_signal.emit(self.interprocess_communication.get_interprocess_communication_file_path_str())  # tell main thread to update its display

        log.info(f"LongTaskWorkerThread.run() took {time.time() - run_start_time} seconds")


class LongTaskRunnin(QMainWindow):

    long_task_file_path_signal = pyqtSignal(str)  # pass file path as a str

    def __init__(self):
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
        self.interprocess_communications_file_path_display = QLineEdit()
        self.interprocess_communications_file_path_display.setReadOnly(True)
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
        layout.addWidget(self.interprocess_communications_file_path_display)
        layout.addWidget(self.start_button)
        layout.addWidget(self.do_something_interactive_button)
        layout.addWidget(self.quit_button)

        self.frame.setLayout(layout)
        self.show()

        self.long_task_worker_thread = None

        self.long_task_file_path_signal.connect(self.display_e_info)  # when the worker process is finished this will be "signaled"

    def check_result(self):
        if self.e is None:
            log.error("Tried to check the result, but the calculation of e has not yet been run.")
        else:
            assert math.isclose(self.e, math.e, rel_tol=0.01)

    def display_e_info(self, interprocess_communication_file_path_str: str):
        """
        Display the "e" values once they've been calculated
        """
        e_info = interprocess_communication_read(interprocess_communication_file_path_str)
        self.e = e_info.e_value
        self.duration_display.setText(str(e_info.duration))
        self.e_display.setText(str(e_info.e_value))
        self.iterations_display.setText(str(e_info.iterations))

    def long_task_runnin_start(self):
        # start doing the work
        if self.long_task_worker_thread is not None and self.long_task_worker_thread.isRunning():
            log.warning("already running")
        else:
            self.long_task_worker_thread = LongTaskWorkerThread(self.long_task_file_path_signal)
            self.interprocess_communications_file_path_display.setText(self.long_task_worker_thread.interprocess_communication.get_interprocess_communication_file_path_str())
            self.long_task_worker_thread.start()

    def interactive_button(self):
        # do something interactive to make sure the UI is working
        self.do_something_interactive_button.setText(f"I've been clicked! ({self.do_something_interactive_button_count=})")
        self.do_something_interactive_button_count += 1

    def long_task_runnin_quit(self):
        # quit the app
        if self.long_task_worker_thread is not None:
            log.debug(f"{self.long_task_worker_thread.isRunning()=}")
            self.long_task_worker_thread.wait()  # make sure the worker thread is done
            log.debug(f"{self.long_task_worker_thread.isRunning()=}")
        self.check_result()
        self.close()

    def long_task_runnin_is_closed(self):
        # for pytest-qt
        assert not self.isVisible()

