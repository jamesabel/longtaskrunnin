import time
import uuid
from multiprocessing import Process


from PyQt5.Qt import pyqtSignal, QThread
from PyQt5.QtWidgets import QMainWindow, QFrame, QVBoxLayout, QLineEdit, QLabel, QPushButton

from longtaskrunnin import application_name, EInfo, InterprocessCommunication


# change these to run the various experiments
use_process = True
force_error = False

time_start = time.time()


def options_str() -> str:
    return f"{use_process=},{force_error=}"


class LongTaskWorkerProcess(Process):
    """
    Run the worker as a Process. This also enabled parallelism (that running as a thread would not).
    """

    def __init__(self, interprocess_communication: InterprocessCommunication, requested_duration: float = 7.0):
        self.interprocess_communication = interprocess_communication
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
        self.interprocess_communication.write(e_info)


class LongTaskWorkerThread(QThread):
    """
    This thread connects the UI to the worker.
    """

    def __init__(self, long_task_signal: pyqtSignal):
        self._long_task_signal = long_task_signal
        self._e_info_interprocess_communication = InterprocessCommunication()
        super().__init__()

    def run(self):
        long_task_worker_process = LongTaskWorkerProcess(self._e_info_interprocess_communication)
        if use_process:
            long_task_worker_process.start()
            long_task_worker_process.join()
        else:
            # Just use LongTaskWorkerProcess() as a (blocking) function. This works, but if there's an error this app just crashes with
            # a `Process finished with exit code -1073740791 (0xC0000409)` instead of a proper Python error message.
            long_task_worker_process.run()

        e_info = self._e_info_interprocess_communication.read()  # get the worker's result - (only works for one call to facilitate cleanup)
        self._long_task_signal.emit(e_info)  # tell main thread to update its display


class LongTaskRunnin(QMainWindow):

    long_task_signal = pyqtSignal(EInfo)

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
        self.do_something_interactive_button.clicked.connect(self.interactive_button)
        self.do_something_interactive_button_count = 0
        layout.addWidget(QLabel(f"{use_process=}"))
        layout.addWidget(QLabel(f"{force_error=}"))
        layout.addWidget(self.duration_display)
        layout.addWidget(self.e_display)
        layout.addWidget(self.iterations_display)
        layout.addWidget(self.do_something_interactive_button)
        self.frame.setLayout(layout)
        self.show()

        self.long_task_signal.connect(self.display_e_info)  # when the worker process is finished this will be "signaled"

        # start doing the work
        self.long_task_worker_thread = LongTaskWorkerThread(self.long_task_signal)
        self.long_task_worker_thread.start()

    def display_e_info(self, e_info: EInfo):
        """
        Display the calculated "e" values
        """
        self.duration_display.setText(str(e_info.duration))
        self.e_display.setText(str(e_info.e_value))
        self.iterations_display.setText(str(e_info.iterations))

    def interactive_button(self):
        # do something to make sure the UI is working
        self.do_something_interactive_button.setText(f"I've been clicked! ({self.do_something_interactive_button_count=})")
        self.do_something_interactive_button_count += 1
