#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# import required modules
from PyQt5.QtWidgets import *
import sys
import numpy as np
import pyqtgraph as pg
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from collections import namedtuple



# Main window class
class Window(QMainWindow):

	def __init__(self):
		super().__init__()

		# setting title
		self.setWindowTitle("PyQtGraph")

		# setting geometry
		self.setGeometry(100, 100, 600, 500)
		
		imv = pg.ImageView()
		data = np.random.normal(size=(100, 200, 200))
		imv.setImage(data, xvals=np.linspace(1., 3., data.shape[0]))
        
		imv.ui.histogram.hide()
		imv.ui.roiBtn.hide()
		imv.ui.menuBtn.hide()

		# calling method
		self.UiComponents(imv)

		# showing all the widgets
		self.show()

	# method for components
	def UiComponents(self, imv):
		widget = QWidget()
		label = QLabel("Geeksforgeeks Image View")
		layout = QGridLayout()
		label.setFixedWidth(130)
		widget.setLayout(layout)
		layout.addWidget(label, 1, 0)
		layout.addWidget(imv, 0, 1, 3, 1)
		self.setCentralWidget(widget)        
		


		
# Driver Code

# create pyqt5 app
App = QApplication(sys.argv)

# create the instance of our Window
window = Window()

# start the app
sys.exit(App.exec())
