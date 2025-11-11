from PyQt5.QtCore import *


class ThreadWorker(QObject):
    finished = pyqtSignal()
    main = None
    th = None
    objects = None  # argument passed to the worker

    def __init__(self, th, main, objects=None):
        super(ThreadWorker, self).__init__()
        self.main = main
        self.th = th
        self.objects = objects

    def run(self):
        # Worker runs some code "here" in the children classes
        if self.th is not None:
            self.th.end_thread_signal.emit()
            self.finished.emit()
