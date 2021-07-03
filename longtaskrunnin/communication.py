import shelve
from pathlib import Path
from typing import Union
from tempfile import mkdtemp

from balsa import get_logger

from longtaskrunnin import application_name, EInfo, rmdir

shelf_key = "e"  # can be anything since we only have one data element in the shelf

log = get_logger(application_name)


class EInfoInterprocessCommunication:
    """
    Provide inter-process communication via shelve.
    """
    def __init__(self):
        self.interprocess_communication_directory = Path(mkdtemp())

    def write_e_info(self, e_info: EInfo):
        # "write back" the result via a shelf
        with shelve.open(str(self.get_interprocess_communication_file_path(self.interprocess_communication_directory))) as shelf:
            shelf[shelf_key] = e_info

    def get_interprocess_communication_file_path(self, interprocess_communication_directory: Path) -> Path:
        interprocess_communication_file_path = Path(interprocess_communication_directory, application_name)
        log.info(f"{interprocess_communication_file_path=}")  # when this is called as part of the Process, it will use that process's logger
        return interprocess_communication_file_path

    def read(self) -> Union[EInfo, None]:
        # read the data (only works once in order to clean up temp files)
        interprocess_communication_file_path = self.get_interprocess_communication_file_path(self.interprocess_communication_directory)
        try:
            with shelve.open(str(interprocess_communication_file_path)) as shelf:
                if (e_info := shelf.get(shelf_key)) is None:
                    s = f"e_info not found at {interprocess_communication_file_path=}"
                    log.error(s)
            rmdir(self.interprocess_communication_directory)  # clean up
        except (FileNotFoundError, IOError):
            log.warning(f"e_info not found at {interprocess_communication_file_path=}")
            e_info = None
        return e_info
