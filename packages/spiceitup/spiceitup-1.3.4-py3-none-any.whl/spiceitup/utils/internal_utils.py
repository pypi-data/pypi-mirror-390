#!/usr/bin/env python3
import time

from PyQt5.QtGui import QFont

from PyQt5 import QtCore, sip
from PyQt5.QtWidgets import *
import numpy as np
from matplotlib import pyplot as plt
import pyqtgraph as pg
from ..settings.const import Const

# ------------- Python utils

def setFontSize(qlabel, font_size): # font_size default is 11
    font = QFont()
    font.setPointSize(font_size)
    qlabel.setFont(font)

def setFontSizes(qlabels, font_size):
    for qlabel in qlabels:
        setFontSize(qlabel, font_size)

def get_ms():
    """Get milliseconds time"""
    return round(time.time() * 1000)



def isClassName(obj, class_name):
    return type(obj).__name__ == class_name


def apply_on_elements_3D(np_array, function_to_apply):
    """ Apply function_to_apply on the elements of a 3-dimension numpy array"""
    func = lambda i: function_to_apply(i)
    vectorized = np.vectorize(func)
    return vectorized(np_array)


def plt_show(np_data):
    """ Allow to quickly show an image thanks to matplotlib (debug purposes)"""
    plt.imshow(np_data, interpolation='nearest')
    plt.show()


# ------------- Calculation custom utils


def win_w(pc):
    """ Returns pc % of the window width in pixels"""
    return int(float(pc) * Const.window_width)


def win_h(pc):
    """ Returns pc % of the window height in pixels"""
    return int(float(pc) * Const.window_height)


def split_w_pc(pc):
    """ Returns a list of 2 elements where the first one contains pc % of the
    window width (pixels) and the second one the rest to fill the window"""
    p = float(pc)
    p_rest = 1 - pc
    return [int(p * Const.window_width), int(p_rest * Const.window_width)]


def split_h_pc(pc):
    """ Returns a list of 2 elements where the first one contains pc % of the
    window height (pixels) and the second one the rest to fill the window"""
    p = float(pc)
    p_rest = 1 - pc
    return [int(p * Const.window_height), int(p_rest * Const.window_height)]


# ------------- Qt custom utils


def get_icon(icon_name): # icon_name == 'SP_something'
    """Get the QIcon related to the built-in icon's name, see toolbox/icons.png and show_icons.py"""
    #icons = sorted([attr for attr in dir(QStyle) if attr.startswith("SP_")]) # shows available icon names
    w_obj = QWidget()
    return w_obj.style().standardIcon(getattr(QStyle, icon_name))


def set_QMessageBox_width(box, width):
    """Change the QMessageBox width, the hack is to add a widget"""
    layout = box.layout()
    item = layout.itemAtPosition(0, 2)
    widget = item.widget()
    widget.setFixedWidth(width)


def show_message(title, msg, width=None):
    """Show a classic alert message box"""
    w_msg = QMessageBox()
    w_msg.setIcon(QMessageBox.Information)
    w_msg.setWindowTitle(title)
    w_msg.setText(msg)
    if width is not None:
        set_QMessageBox_width(w_msg, width)
    w_msg.exec_()


def get_cross_pen(mouse_hover=False, map_background='#000000', force_color=None):
    color = force_color if force_color is not None else Const.cross_bar_color[map_background]
    width = Const.cross_bar_width_hover if mouse_hover else Const.cross_bar_width
    return pg.mkPen(color, width=width)


def set_tooltip(widget, text):
    widget.setToolTip(text)

def show_message_table(title, msg, dict_, width=None, height=None, colored_text=True, detailed_text=None):
    w_msg = QMessageBox()
    w_msg.setIcon(QMessageBox.Information)
    w_msg.setWindowTitle(title)
    if detailed_text is not None:
        w_msg.setDetailedText(detailed_text)
    if width is not None:
        set_QMessageBox_width(w_msg, width)
    msg_layout = w_msg.layout()

    f_inside = QFrame()
    w_scroll = QScrollArea()
    w_scroll.setWidget(f_inside)
    w_scroll.setWidgetResizable(True)
    w_scroll.setFixedWidth(width + 100)
    if height is not None:
        w_scroll.setFixedHeight(height)
    new_layout = QGridLayout(f_inside)
    c = ''
    ec = ''
    if colored_text:
        c = Const.colored_text
        ec = Const.end_colored_text
    q_msg = QLabel(msg)
    q_msg.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
    new_layout.addWidget(q_msg, 0, 0, 1, 2)
    i = 1
    for key, val in dict_.items():
        if val == '':  # title
            q_title = QLabel('&rarr; <b>' + str(key) + '</b>')
            q_title.setStyleSheet('margin-top: 10px;')
            new_layout.addWidget(q_title, i, 0, 1, 2)
        else:
            new_layout.addWidget(QLabel(key), i, 0, 1, 1)
            q_val = QLabel(c + str(val) + ec)
            q_val.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
            new_layout.addWidget(q_val, i, 1, 1, 1)
        i += 1

    msg_layout.addWidget(w_scroll)
    w_msg.exec_()


def clearLayout(layout):
    """Remove all widgets and spaces in a layout"""
    if layout is not None:
        for i in reversed(range(layout.count())): 
            layout.takeAt(i).widget().setParent(None)


def deleteLayout(cur_lay):
    """Delete a whole layout"""
    #QtGui.QLayout(cur_lay)
    
    if cur_lay is not None:
        while cur_lay.count():
            item = cur_lay.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                deleteLayout(item.layout())
        sip.delete(cur_lay)


def toggleCheckbox(qcheckbox):
    """Check or uncheck a QCheckbox (change the state)"""
    qcheckbox.setChecked(not qcheckbox.isChecked())


def asText(list_, sep = ', '):
    txt = ''
    for el in list_:
        txt += el + sep
    return txt[0:len(txt) - len(sep)]
