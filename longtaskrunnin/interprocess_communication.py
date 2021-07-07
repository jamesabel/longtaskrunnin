import pickle
from pathlib import Path
from tempfile import mkdtemp
from typing import Any

from balsa import get_logger

from longtaskrunnin import rmdir

log = get_logger(__name__)


class InterprocessCommunication:
    """
    Provide generic inter-process communication via pickle. Can be used to return results from a multiprocessing.Process() instance.
    """
    def __init__(self):
        self.interprocess_communication_directory = Path(mkdtemp())
        self.interprocess_communication_file_path = Path(self.interprocess_communication_directory, "data.pickle")

    def write(self, data: Any):
        """
        write the result

        :param data: data to write, which will be passed to another process
        """
        with open(self.interprocess_communication_file_path, "wb") as pickle_file:
            pickle.dump(data, pickle_file)

    def get_interprocess_communication_file_path_str(self) -> str:
        return str(self.interprocess_communication_file_path)


def interprocess_communication_read(interprocess_communication_file_path_str: str) -> Any:
    """
    Read the data. Must be called exactly once in order to get the data and clean up temp files.

    :return: data from the .write() call
    """
    interprocess_communication_file_path = Path(interprocess_communication_file_path_str)
    assert interprocess_communication_file_path.exists()
    assert interprocess_communication_file_path.is_file()
    with open(interprocess_communication_file_path, "rb") as pickle_file:
        data = pickle.load(pickle_file)
    rmdir(interprocess_communication_file_path.parent)  # clean up
    return data
