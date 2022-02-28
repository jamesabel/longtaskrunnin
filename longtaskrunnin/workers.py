import time
import uuid
from multiprocessing import Process, SimpleQueue
from typing import Dict, Any

from PyQt5.QtCore import QThread, pyqtSignal
from balsa import balsa_clone, get_logger

from longtaskrunnin import EInfo, force_error, use_process, application_name, use_process_logger

log = get_logger(application_name)


class LongTaskWorkerProcess(Process):
    """
    Run the worker as a Process. This also enabled parallelism (that running as a thread would not).
    """

    def __init__(self, log_config_as_dict: Dict[str, Any], requested_duration: float = 3.0):
        self._log_config_as_dict = log_config_as_dict
        self._requested_duration = requested_duration
        self._result_queue = SimpleQueue()
        self._result = None
        super().__init__(name="LongTaskWorkerProcess")  # if you have more than one process, each name must be unique

    def run(self):
        """
        Waste some time by calculating the "e" by iteration. Return an object that is relatively arbitrary in contents and size
        (as opposed to, say, a simple float).
        """

        # must be done in the run() method (not __init__() )
        if use_process_logger:
            balsa = balsa_clone(self._log_config_as_dict, self.name)
            balsa.init_logger()
            _log = balsa.log
        else:
            # normal logger, but this gets no configuration so only warning and higher are logged, and they go to stdout
            _log = log

        _log.debug(f"LongTaskWorkerProcess entering run()")

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
        self._result_queue.put(e_info)  # pass back result

        # This will be written to the process's log file, which is different from the regular log file to avoid file write contention.
        _log.debug(f"LongTaskWorkerProcess exiting run()")
        run_time_string = f"LongTaskWorkerProcess.run() took {time.time() - run_start_time} seconds"
        if use_process_logger:
            _log.info(run_time_string)
        else:
            _log.error(run_time_string)  # not really an error, but it has to be warning or above to be output with the default log settings

    def get_result(self) -> EInfo:
        """
        Get the result. Can be called multiple times.
        Note that using a method to get the result allows the result to be typed to the consumer of this class.
        :return: "e" info
        """

        if self._result is None:
            self.join()
            self._result = self._result_queue.get()
        return self._result


class LongTaskWorkerThread(QThread):
    """
    This thread connects the UI to the worker.
    """

    def __init__(self, long_task_signal: pyqtSignal, log_config_as_dict: Dict[str, Any]):
        self._long_task_signal = long_task_signal
        self._log_config_as_dict = log_config_as_dict
        self.return_value = None
        super().__init__()

    def run(self):
        run_start_time = time.time()

        # will be written to the regular log file
        log.debug(f"LongTaskWorkerThread entering run()")

        long_task_worker_process = LongTaskWorkerProcess(self._log_config_as_dict)
        if use_process:
            long_task_worker_process.start()
        else:
            # Just use LongTaskWorkerProcess() as a (blocking) function. This works, but if there's an error this app just crashes with
            # a `Process finished with exit code -1073740791 (0xC0000409)` instead of a proper Python error message.
            long_task_worker_process.run()

        self.return_value = long_task_worker_process.get_result()
        self._long_task_signal.emit(self.return_value)  # tell main thread to update its display

        log.debug(f"LongTaskWorkerThread exiting run()")
        log.info(f"LongTaskWorkerThread.run() took {time.time() - run_start_time} seconds")
