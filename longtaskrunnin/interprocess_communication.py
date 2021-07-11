import pickle
from pathlib import Path
from tempfile import mkdtemp
from typing import Any
from os import fspath

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
        write the data for reading later

        :param data: data to write, which will be passed to another process
        """
        with open(self.interprocess_communication_file_path, "wb") as pickle_file:
            pickle.dump(data, pickle_file)

    def get_interprocess_communication_file_path_str(self) -> str:
        """
        Get the interprocess communication file path as a str
        :return: interprocess communication file path as a str
        """

        # Python tip: anytime you accept a path that could be a path-like object (e.g. pathlib), never rely on its string repr; always use os.fsdecode(), os.fsencode(), or os.fspath().
        # https://twitter.com/brettsky/status/1404521184008413184
        return fspath(self.interprocess_communication_file_path)


def interprocess_communication_read(interprocess_communication_file_path_str: str) -> Any:
    """
    Read the data. Must be called exactly once in order to get the data and clean up temp files.

    :return: data from the InterprocessCommunication.write() call
    """
    data = None
    interprocess_communication_file_path = Path(interprocess_communication_file_path_str)

    # Log errors and return a None instead of taking an exception since PyQt can merely crash on an exception in a thread.
    if not interprocess_communication_file_path.exists():
        log.error(f"{interprocess_communication_file_path} does not exist")
    elif not interprocess_communication_file_path.is_file():
        log.error(f"{interprocess_communication_file_path} is not a file")
    else:
        with open(interprocess_communication_file_path, "rb") as pickle_file:
            data = pickle.load(pickle_file)
        rmdir(interprocess_communication_file_path.parent)  # clean up
    return data
