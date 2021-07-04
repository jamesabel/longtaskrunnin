import pickle
from pathlib import Path
from tempfile import mkdtemp
from typing import Any

from balsa import get_logger

from longtaskrunnin import application_name, EInfo, rmdir

log = get_logger(application_name)


class EInfoInterprocessCommunication:
    """
    Provide inter-process communication via pickle.
    """
    def __init__(self):
        self.interprocess_communication_directory = Path(mkdtemp())

    def write_e_info(self, data: Any):
        # "write back" the result
        with open(self.get_interprocess_communication_file_path(), "wb") as pickle_file:
            pickle.dump(data, pickle_file)

    def get_interprocess_communication_file_path(self) -> Path:
        interprocess_communication_file_path = Path(self.interprocess_communication_directory, "data.pickle")
        log.debug(f"{interprocess_communication_file_path=}")  # when this is called as part of the Process, it will use that process's logger
        return interprocess_communication_file_path

    def read(self) -> Any:
        # read the data (only works once in order to clean up temp files)
        interprocess_communication_file_path = self.get_interprocess_communication_file_path()
        try:
            with open(interprocess_communication_file_path, "rb") as pickle_file:
                e_info = pickle.load(pickle_file)
            rmdir(self.interprocess_communication_directory)  # clean up
        except (FileNotFoundError, IOError):
            log.warning(f'"{interprocess_communication_file_path}" not found')
            e_info = None
        return e_info
