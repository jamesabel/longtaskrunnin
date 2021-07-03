import sys
from ismain import is_main
from balsa import Balsa, get_logger
from PyQt5.Qt import QApplication

from longtaskrunnin import LongTaskRunnin, application_name, author, options_str

log = get_logger(application_name)

if is_main():

    balsa = Balsa(application_name, author, verbose=True)
    balsa.init_logger()

    print(options_str())
    application = QApplication(sys.argv)
    long_task_running = LongTaskRunnin()
    application.exec_()