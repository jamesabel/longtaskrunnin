import shelve
from pathlib import Path
from tempfile import mkdtemp

from balsa import get_logger

from longtaskrunnin import application_name, EInfo, rmdir

shelf_key = "e"

log = get_logger(application_name)


def write_e_info(interprocess_communication_directory: Path, e_info: EInfo):
    # "write back" the result via a shelf
    with shelve.open(str(get_interprocess_communication_file_path(interprocess_communication_directory))) as shelf:
        shelf[shelf_key] = e_info


def get_interprocess_communication_file_path(interprocess_communication_directory: Path) -> Path:
    interprocess_communication_file_path = Path(interprocess_communication_directory, application_name)
    log.info(f"{interprocess_communication_file_path=}")
    return interprocess_communication_file_path


class EInfoInterprocessCommunication:
    def __init__(self):
        self.communication_directory = Path(mkdtemp())

    def read(self) -> EInfo:
        # read the data (only works once in order to clean up temp files)
        interprocess_communication_file_path = get_interprocess_communication_file_path(self.communication_directory)
        with shelve.open(str(interprocess_communication_file_path)) as shelf:
            if (e_info := shelf.get(shelf_key)) is None:
                s = f"e_info not found at {interprocess_communication_file_path=}"
                log.error(s)
                raise RuntimeError(s)  # this will actually cause a crash when done inside a QThread
        shelf.close()
        rmdir(self.communication_directory)
        print(f"read() : {e_info=}")
        return e_info
