from multiprocessing import Pool
from PyQt5 import uic, QtWidgets
from PyQt5.QtWidgets import *
import sys
import time

def updater(num):
    time.sleep(10)
    print(num)

def main_tracker():
    p = Pool(processes=4)
    data = p.map(updater, range(0, 100))
    p2 = Pool(processes=4)
    data2 = p2.map(updater, range(0, 100))

if __name__ == "__main__":
    app=QtWidgets.QApplication(sys.argv)
    window = uic.loadUi("tracker.ui")
    window.pushButton.clicked.connect(main_tracker)
    window.show()
    sys.exit(app.exec_())
