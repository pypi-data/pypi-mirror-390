#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QKeySequence
from ..settings.const import Const
from PyQt5.QtWidgets import *
from ..processing.dh import DataHandling
from ..utils.internal_utils import *
import os
import pyqtgraph as pg
from ..logs.log import Log
from ..processing.threads.run_thread import RunThread
from ..toolbox.clickable_qlabel import ClickableQLabel
from ..main.winc import WindowsContainer


class Header(QFrame):
    main = None # widget windows visualization (main widget)
    data_path = None
    data_file_basename = None
    w_fits_file_name = None
    rt_recovering = None
    
    def __init__(self, main):
        super(Header, self).__init__()
        self.main = main
        self.setFrameShape(QFrame.StyledPanel)

        self.w_fits_file_name = QLabel('Please load SPICE data (FITS file level 2)')
        self.w_fits_file_name.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        hbox = QHBoxLayout(self)
        img_i = ClickableQLabel()
        img_i.setPixmap(QPixmap('images/info.png'))
        img_i.clicked.connect(self.a_see_details)
        img_i.show()
        set_tooltip(img_i, 'See data file header details')
        hbox.addWidget(img_i)
        hbox.addWidget(self.w_fits_file_name)
        hbox.addStretch(1)

    def cancel_file(self):
        self.main.is_loading_data = False
        if self.rt_recovering is not None:
            self.rt_recovering.interrupt()
        if self.main.dh is not None:  # no data loaded
            self.main.f_menu.enable()
        QApplication.restoreOverrideCursor()
        return

    def a_load_fits(self, data_file_path=False):
        if self.main.is_loading_data:
            show_message('Data file is loading', 'A data file is already loading...')
            return
        self.main.is_loading_data = True
        self.rt_recovering = None
        self.main.f_menu.disable()
        if data_file_path is False:
            self.rt_recovering = RunThread('OutOfSync', self.main, -2, 'Recovering data file on disk',
                                      with_cancel=False)
            q_data_file = QFileDialog.getOpenFileName(self, 'Open file', '', '*.fits')
            self.data_path = q_data_file[0]
            if self.data_path == '':  # cancel
                self.cancel_file()
                return
        else:  # from recent files (or loaded automatically in debug mode)
            self.data_path = data_file_path
        QApplication.setOverrideCursor(Qt.WaitCursor)

        if not os.path.exists(self.data_path):
            self.cancel_file()
            show_message('Data file does not exist', 'This data file does not exist anymore.')
            return
        dh = DataHandling()
        if not dh.load_file(self.main, self.data_path):
            self.cancel_file()
            show_message('Wrong data file', 'The data file could not be loaded, please select a SPICE data'
                                            ' file level 2.')
            return
        self.main.dh = dh

        self.main.f_winc.reset_display_parameters()
        self.data_file_basename = os.path.basename(self.data_path)
        self.w_fits_file_name.setText(self.data_file_basename)

        # Handle study type
        x_y_label = 'I(t, y)' if dh.is_sas else 'I(x, y)'
        fit1_label = 'I(t, y)' if dh.is_sas else 'I(x, y)'
        fit2_label = 'v(t, y)' if dh.is_sas else 'v(x, y)'
        fit3_label = 'σ(t, y)' if dh.is_sas else 'σ(x, y)'
        self.main.f_menu.ks_show_hide['x_y'].setText(x_y_label)
        self.main.f_menu.ks_show_hide['fit_1'].setText('Fit ' + fit1_label)
        self.main.f_menu.ks_show_hide['fit_2'].setText('Fit ' + fit2_label)
        self.main.f_menu.ks_show_hide['fit_3'].setText('Fit ' + fit3_label)
        default_lambda_rescaling = Const.default_lambda_rescaling
        if dh.is_full_spectrum:
            default_lambda_rescaling = 1
        self.main.f_menu.s_lambda_rescaling.setValue(default_lambda_rescaling)

        for plot_key, k_show_hide in self.main.f_menu.ks_show_hide.items():
            if dh.is_full_spectrum:
                self.main.f_menu.ks_show_hide[plot_key].setChecked(plot_key == 'lambda_y')
            else:
                self.main.f_menu.ks_show_hide[plot_key].setChecked('fit' not in plot_key)
                self.main.f_menu.ks_show_hide[plot_key].setEnabled(True)
        self.main.f_menu.q_abscissa_rescaling.setText(dh.x_or_t + ' rescaling')

        nb_windows = len(dh.data_info['win_keys'])
        plur = ''
        if nb_windows > 1:
            plur = 's'
        self.w_fits_file_name.setText(self.w_fits_file_name.text() + ' (' +
                                      str(nb_windows) + ' window' + plur + ')')
        if self.rt_recovering is not None:  # i.e. not from user browse box
            self.rt_recovering.force_success_interruption()
        RunThread('OutOfSync', self.main, 1, 'Loading ' + self.data_file_basename,
                  WindowsContainer.generateWindows, with_cancel=False)
        # Handle recent files
        append_it = True  # will append the file path in the recent files
        if os.path.exists(Const.recent_files_path):
            file = open(Const.recent_files_path, 'r')
            if self.data_path in file.read():
                append_it = False
            file.close()

        if append_it:
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            a = self.main.m_menu_bar.a_no_recent
            if a is not None:
                self.main.m_menu_bar.subm_recent_files.removeAction(a)
                self.main.m_menu_bar.a_no_recent = None
            for action in self.main.m_menu_bar.subm_recent_files.actions():
                action.setShortcut(QKeySequence())
            a_new = self.main.m_menu_bar.subm_recent_files.addAction(now + ' ' + self.data_path)
            a_new.setShortcut('Ctrl+L')
            a_new.triggered.connect(lambda: self.a_load_fits(self.data_path))
            file = open(Const.recent_files_path, 'a')
            file.write('\n' + now + ' ' + self.data_path)
            file.close()

    def a_see_details(self):
        dh = self.main.dh
        details_title = "Data file header"

        if dh is None:  # user did not load a data file yet
            show_message(details_title, 'Load a data file first in order to see the related details.')
        else:
            c = Const.colored_text
            ec = Const.end_colored_text
            msg_text = 'Details for input ' + c + self.main.f_header.data_file_basename + ec
            header = {**dh.get_study_header_detail(), **dh.data_info['study_details']}
            show_message_table(details_title, msg_text, header, 700, 700)
