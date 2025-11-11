#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime
from functools import partial

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

from ..logs.log import Log
from ..processing.threads.run_thread import RunThread
from ..settings.const import Const

class Footer(QFrame):
    main = None
    f_container = None
    progress_lines = []

    def __init__(self, main):
        super(Footer, self).__init__()
        self.main = main
        self.setFrameShape(QFrame.StyledPanel)

        l_footer = QVBoxLayout(self)
        self.f_container = QFrame()

        w_scroll = QScrollArea()
        w_scroll.setWidget(self.f_container)
        w_scroll.setWidgetResizable(True)
        l_footer.addWidget(w_scroll)

        self.l_grid = QGridLayout()
        self.l_grid.setVerticalSpacing(5)

        self.f_container.setLayout(self.l_grid)

    def show_progress_line(self, index):
        for key, widget in self.progress_lines[index].items():
            if not isinstance(widget, int) and not isinstance(widget, str):  # exclude index/line and title text
                widget.show()

    def hide_progress_line(self, index):
        for key, widget in self.progress_lines[index].items():
            if not isinstance(widget, int) and not isinstance(widget, str): # exclude index/line and title text
                widget.hide()

    def get_color(self, val):
        color = Const.progress_bar_color
        if val == 100:
            color = Const.progress_bar_color_done
        return color

    def get_text_color(self, val):
        color = Const.progress_bar_color
        if val == 100:
            color = Const.green_text
        return color

    def get_progress_line_index(self, id_):
        for index, pl in enumerate(self.progress_lines):
            if pl['id'] == id_:
                return index

    def update_progress_line_by_id(self, id_, val):
        index = self.get_progress_line_index(id_)
        self.update_progress_line(index, val)

    def interrupt_progress_line_by_id(self, id_):
        index = self.get_progress_line_index(id_)
        self.interrupt_progress_line(index)

    def interrupt_processes(self):
        for index, pl in enumerate(self.progress_lines):
            if pl['val'] < 100:
                self.interrupt_progress_line(index)

    def interrupt_progress_line(self, index):
        color = Const.progress_bar_interrupt_color
        text_color = Const.red_text
        self.progress_lines[index]['interrupted'] = True
        self.progress_lines[index]['pb'].setStyleSheet('QProgressBar::chunk { background-color: ' +
                                                       color + ';}')
        self.progress_lines[index]['pb2'].setStyleSheet('QProgressBar::chunk { background-color: ' +
                                                        color + ';}')
        self.progress_lines[index]['q_title'].setText('<font color="' + text_color + '">' +
                                                      self.progress_lines[index]['title'] + '</font>')
        val = self.progress_lines[index]['val']
        val_str = '-'
        if val != 1:
            val_str = str(val) + ' %'
        self.progress_lines[index]['q_pc'].setText('<font color="' + text_color + '"><b>' +
                                                   val_str + '</b></font>')
        self.progress_lines[index]['b_cancel'].setText('Cancelled')

    def update_progress_line(self, index, val, new_line=False):  # Use update_progress_line_by_id from outside instead
        # because lines are continuously changing here (adding one moves the other ones)
        if self.progress_lines[index]['interrupted'] and not new_line and val < 100:
            color = Const.progress_bar_interrupt_color
            text_color = Const.red_text
        else:
            color = self.get_color(val)
            text_color = self.get_text_color(val)
        self.progress_lines[index]['pb'].setStyleSheet('QProgressBar::chunk { background-color: ' +
                                                       color + ';}')
        self.progress_lines[index]['pb2'].setStyleSheet('QProgressBar::chunk { background-color: ' +
                                                        color + ';}')
        if val > 100:
            Log.p('Warning: value greater than 100% given (' + str(val) + '), set to 100.')
            val = 100

        # Setting up both sliders
        val1 = val * 2
        if val1 > 100:
            val1 = 100
        val2 = 2 * (val - 50)
        if val2 < 0:
            val2 = 0
        val_str = '-'
        if val != 1:
            val_str = str(val) + ' %'
        self.progress_lines[index]['pb'].setValue(val1)
        self.progress_lines[index]['pb2'].setValue(val2)
        self.progress_lines[index]['q_title'].setText('<font color="' + text_color + '">' +
                                                      self.progress_lines[index]['title'] + '</font>')
        self.progress_lines[index]['q_pc'].setText('<font color="' + text_color + '"><b>' +
                                                   val_str + '</b></font>')
        self.progress_lines[index]['val'] = val

        if not new_line:
            pl_from = self.progress_lines[index]
            pl_from['val'] = val
            self.update_cancel_button(pl_from, self.progress_lines[index])
            rt = self.progress_lines[index]['rt']
            b_cancel = self.progress_lines[index]['b_cancel']
            try:
                b_cancel.clicked.disconnect()
            except TypeError:  # this one was not connected
                pass
            b_cancel.clicked.connect(partial(Footer.interrupt,
                                             b_cancel,
                                             rt))

    def change_line(self, index, pl):
        val = self.progress_lines[index]['val']
        if pl['interrupted']:
            text_color = Const.red_text
        else:
            text_color = self.get_text_color(val)
        self.progress_lines[index]['title'] = pl['title']
        self.progress_lines[index]['q_title'].setText('<font color="' + text_color + '">' +
                                                      pl['title'] + '</font>')
        self.progress_lines[index]['interrupted'] = pl['interrupted']
        self.progress_lines[index]['with_cancel'] = pl['with_cancel']
        self.update_cancel_button(pl, self.progress_lines[index])
        self.progress_lines[index]['rt'] = pl['rt']

    def update_cancel_button(self, pl_from, pl_to):
        if pl_to['val'] is not None:
            is_done = pl_to['val'] >= 100
            must_be_enabled = pl_from['with_cancel'] and not pl_from['interrupted'] and not is_done
            pl_to['b_cancel'].setEnabled(must_be_enabled)
            cancel_text = 'Cancel'
            if is_done:
                cancel_text = 'Done'
            elif pl_from['interrupted']:
                cancel_text = 'Cancelled'
            button_css = Const.footer_button + ' '
            button_css += Const.button_enabled if must_be_enabled else Const.button_disabled
            pl_to['b_cancel'].setStyleSheet(button_css)
            pl_to['b_cancel'].setText(cancel_text)

    @staticmethod
    def interrupt(b_cancel, rt):
        b_cancel.setText('Cancelled')
        b_cancel.setEnabled(False)
        b_cancel.setStyleSheet(Const.footer_button + ' ' + Const.button_disabled)
        rt.interrupt()

    def create_progress_line(self, rt, title, with_cancel=True):
        now = datetime.now()
        title = 'At ' + now.strftime('%H:%M:%S') + ' - ' + title
        q_title = QLabel()
        q_pc = QLabel('')
        q_pc.setAlignment(Qt.AlignCenter)
        pb = QProgressBar()
        pb.setFixedHeight(Const.progress_bar_height)
        pb.setTextVisible(False)
        pb2 = QProgressBar()
        pb2.setFixedHeight(Const.progress_bar_height)
        pb2.setTextVisible(False)
        b_cancel = QPushButton('Cancel')
        if with_cancel:
            b_cancel.setStyleSheet(Const.footer_button + ' ' + Const.button_enabled)
        else:
            b_cancel.setStyleSheet(Const.footer_button + ' ' + Const.button_disabled)
            b_cancel.setEnabled(False)

        new_index = len(self.progress_lines)

        self.l_grid.addWidget(q_title, new_index, 0)
        self.l_grid.addWidget(pb, new_index, 1)
        self.l_grid.addWidget(q_pc, new_index, 2)
        self.l_grid.addWidget(pb2, new_index, 3)
        self.l_grid.addWidget(b_cancel, new_index, 4)

        # will be erased but create permanent objects (bars, labels, button)
        self.progress_lines.append({'id': '', 'title': '', 'q_title': q_title, 'with_cancel': None,
                                    'pb': pb, 'q_pc': q_pc, 'pb2': pb2, 'val': None,
                                    'interrupted': None, 'b_cancel': b_cancel, 'rt': None})

        if new_index > 0:
            # Push other lines to free the first line
            for i in reversed(range(new_index)):
                # Copying i into (i + 1)
                self.progress_lines[i + 1]['id'] = self.progress_lines[i]['id']
                self.change_line(i + 1, self.progress_lines[i])
                self.update_progress_line(i + 1, self.progress_lines[i]['val'])

        # Now line 0 is available
        self.update_progress_line(0, 0, True)
        self.change_line(0, {'title': title, 'interrupted': False, 'with_cancel': with_cancel,
                                      'b_cancel': b_cancel, 'rt': rt})
        self.progress_lines[0]['id'] = new_index
        if with_cancel:
            self.progress_lines[0]['b_cancel'].clicked.connect(partial(Footer.interrupt,
                                                                       self.progress_lines[0]['b_cancel'],
                                                                       rt))

        return new_index  # created id

