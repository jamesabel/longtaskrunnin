import time
import uuid
from pathlib import Path
from multiprocessing import Process


from PyQt5.Qt import pyqtSignal, QThread
from PyQt5.QtWidgets import QMainWindow, QFrame, QVBoxLayout, QLineEdit, QLabel, QPushButton

from longtaskrunnin import application_name, EInfo, EInfoInterprocessCommunication, write_e_info, get_interprocess_communication_file_path


# change these to run the various experiments
use_process = True
force_error = False

time_start = time.time()


def options_str() -> str:
    return f"{use_process=},{force_error=}"


class LongTaskWorkerProcess(Process):

    def __init__(self, interprocess_communication_directory_path: Path, requested_duration: float = 7.0):
        self.interprocess_communication_directory_path = interprocess_communication_directory_path
        self.requested_duration = requested_duration
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
            div_error_value = 1.0/0.0

        k = 1.0
        while time.time() - run_start_time < self.requested_duration:
            e_info.e_value += 1.0 / k
            k *= e_info.iterations + 1
            e_info.iterations += 1
            e_info.duration = time.time() - run_start_time
        write_e_info(self.interprocess_communication_directory_path, e_info)
        print(f"from LongTaskWorkerProcess {time.time() - time_start} {time.time() - run_start_time}")

    # def get_e_info(self) -> EInfo:
    #     return self.e_info


class LongTaskWorkerThread(QThread):

    def __init__(self, long_task_signal: pyqtSignal):
        self.long_task_signal = long_task_signal
        self.e_info_interprocess_communication = EInfoInterprocessCommunication()
        super().__init__()

    def run(self):
        long_task_worker_process = LongTaskWorkerProcess(self.e_info_interprocess_communication.communication_directory)
        print(f"from LongTaskWorkerThread {time.time() - time_start}")
        if use_process:
            long_task_worker_process.start()
            long_task_worker_process.join()
        else:
            long_task_worker_process.run()  # use LongTaskWorkerProcess() as a function (will block)
        print(f"from LongTaskWorkerThread {time.time() - time_start}")

        self.long_task_signal.emit()  # tell main thread to update its display (data returned via shelf)
        # self.long_task_signal.emit(long_task_worker_process.get_e_info())  # tell main thread to update its display with this value


class LongTaskRunnin(QMainWindow):

    long_task_signal = pyqtSignal()  # signal merely tells the UI to update - the actual values are passed via shelf
    # long_task_signal = pyqtSignal(EInfo)  # when trying to pass the resultant value via signal

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
        self.do_something_interactive_button = QPushButton("Click me")
        self.do_something_interactive_button.clicked.connect(self.ran_ok)
        self.do_something_interactive_button_count = 0
        layout.addWidget(QLabel(f"{use_process=}"))
        layout.addWidget(QLabel(f"{force_error=}"))
        layout.addWidget(self.duration_display)
        layout.addWidget(self.e_display)
        layout.addWidget(self.iterations_display)
        layout.addWidget(self.do_something_interactive_button)
        self.frame.setLayout(layout)
        self.show()

        self.long_task_signal.connect(self.display_e_info)

        if True:
            # QThread (which uses Process)
            self.long_task_worker_thread = LongTaskWorkerThread(self.long_task_signal)
            self.long_task_worker_thread.start()
        else:
            # Process (only). Use to create:
            # TypeError: cannot pickle 'PyQt5.QtCore.pyqtBoundSignal' object
            long_task_worker_process = LongTaskWorkerProcess(self.long_task_signal)
            long_task_worker_process.start()
            long_task_worker_process.join()

    # def display_e_info(self, e_info: EInfo):  # data via pyqtSignal
    def display_e_info(self):  # data via shelf
        e_info = self.long_task_worker_thread.e_info_interprocess_communication.read()  # only works once (to facilitate cleanup)
        print(f"from display_e_info {time.time() - time_start} {e_info=}")
        self.duration_display.setText(str(e_info.duration))
        self.e_display.setText(str(e_info.e_value))
        self.iterations_display.setText(str(e_info.iterations))

    def ran_ok(self):
        # do something to make sure the UI is working
        self.do_something_interactive_button.setText(f"I've been clicked! ({self.do_something_interactive_button_count=})")
        self.do_something_interactive_button_count += 1
