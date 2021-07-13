import sys
from ismain import is_main
from balsa import Balsa, get_logger
from PyQt5.Qt import QApplication

from longtaskrunnin import LongTaskRunnin, application_name, author, options_str

log = get_logger(application_name)

if is_main():

    balsa = Balsa(application_name, author, verbose=False)
    balsa.init_logger()

    application = QApplication(sys.argv)
    long_task_runnin = LongTaskRunnin()
    application.exec_()
