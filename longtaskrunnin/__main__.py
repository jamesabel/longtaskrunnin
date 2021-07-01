import sys
from ismain import is_main
from balsa import Balsa
from PyQt5.Qt import QApplication

from longtaskrunnin import LongTaskRunnin, application_name, author

if is_main():

    balsa = Balsa(application_name, author)
    balsa.init_logger()

    application = QApplication(sys.argv)
    long_task_running = LongTaskRunnin()
    application.exec_()
