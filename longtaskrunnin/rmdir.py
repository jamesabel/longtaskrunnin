import os
import stat
import time
import shutil
from pathlib import Path

from balsa import get_logger

from longtaskrunnin import application_name

log = get_logger(application_name)


def remove_readonly(path):
    os.chmod(path, stat.S_IWRITE)


# sometimes needed for Windows
def _remove_readonly_onerror(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)


def rmdir(p: Path, log_function=log.error) -> bool:
    """
    robust remove directory

    :param p: directory to remove
    :param log_function: log function to use for error
    :return: True if deleted OK, False if error
    """
    retry_count = 0
    retry_limit = 4
    delete_ok = False
    delay = 1.0
    while os.path.exists(p) and retry_count < retry_limit:
        try:
            shutil.rmtree(p, onerror=_remove_readonly_onerror)
            delete_ok = True
        except FileNotFoundError as e:
            log.debug(str(e))  # this can happen when first doing the shutil.rmtree()
            time.sleep(delay)
        except PermissionError as e:
            log.info(str(e))
            time.sleep(delay)
        except OSError as e:
            log.info(str(e))
            time.sleep(delay)
        time.sleep(0.1)
        if os.path.exists(p):
            time.sleep(delay)
        retry_count += 1
        delay *= 2.0
    if os.path.exists(p):
        log_function(f"could not remove {p} ({retry_count=})", stack_info=True)
    else:
        delete_ok = True
    return delete_ok
