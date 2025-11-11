class ThreadClass(QtCore.QThread):
    # Create the signal
    sig = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        super(ThreadClass, self).__init__(parent)

        # Connect signal to the desired function
        self.sig.connect(updateProgBar)

    def run(self):
        while True:
            val = sysInfo.getCpu()

            # Emit the signal
            self.sig.emit(val)