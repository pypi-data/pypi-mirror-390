import sys
import numpy as np
import pyqtgraph as pg
from PyQt5.QtGui import *
import random

from PyQt5.QtWidgets import *


class Main(QMainWindow):
    def __init__(self, parent = None):
        super(QMainWindow, self).__init__(parent)
        self.wp = pg.GraphicsLayoutWidget()
        self.iv = pg.ImageView(parent=self.wp, view=pg.PlotItem())
        self.main_plot_item.invertY(False)
        np_data = np.array([[1,2,3],[4,5,6]])
        self.iv.setImage(np_data, xvals=np.linspace(0., np_data.shape[0], np_data.shape[0]))
        tr = QTransform()
        tr.translate(5, 10)
        self.ii.setTransform(tr)
        self.iv.setPredefinedGradient('viridis')
        self.iv.show()

        self.scene = self.main_plot_item.scene()  # GraphicsScene
        self.scene.sigMouseMoved.connect(self.a_mouse_moved)
        self.scene.sigMouseClicked.connect(self.a_mouse_clicked)

        central_widget = QFrame()
        self.setCentralWidget(central_widget)
        hbox = QHBoxLayout(central_widget)
        hbox.addWidget(self.wp)
        self.b = QPushButton('setImage(...)')
        self.b.clicked.connect(self.a)
        hbox.addWidget(self.b)
        self.a()

        print(self.main_plot_item.pixelSize())

    @property
    def ii(self):
        return self.iv.getImageItem()

    def apply_transform(self):
        step = 4
        self.main_plot_item.getAxis('bottom').setScale(3. / step)

        tr = QTransform()
        tr.scale(step, 1)
        #if self.plot_key == 'x_y' or self.plot_key == 'lambda_y' or 'fit' in self.plot_key:
        tr.translate(5-0.5, -0.5)  # even with step > 1, because of previous scale, offsetting x - 0.5 is fine
        self.ii.setTransform(tr)

    def a_mouse_moved(self, point):
        p = self.main_plot_item.vb.mapSceneToView(point)
        self.mouse_x = int(round(float(p.x())))
        self.mouse_y = int(round(float(p.y())))

    def a_mouse_clicked(self):
        print(self.mouse_x, self.mouse_y)

    @property
    def main_view_box(self):
        return self.ii.getViewBox()

    @property
    def main_plot_item(self):
        return self.iv.getView()

    def a(self):
        np_data = np.array([[random.randint(0,90),random.randint(0,90),random.randint(0,90)], \
                            [random.randint(0,90),random.randint(0,90),random.randint(0,90)],
                            [random.randint(0,90),random.randint(0,90),random.randint(0,90)]])
        state = self.main_plot_item.getViewBox().getState(True)
        self.iv.setImage(np_data, xvals=np.linspace(0., np_data.shape[0], np_data.shape[0]))
        self.apply_transform()
        self.main_plot_item.getViewBox().setState(state)
        self.iv.autoRange() # view all
        #self.iv.autoLevels()

if __name__ == "__main__":
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()

    win = Main()
    win.resize(1600, 800)
    win.setWindowIcon(QIcon('images/icon.png'))
    win.show()

    sys.exit(app.exec())
