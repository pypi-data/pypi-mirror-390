#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import *

from ..utils.internal_utils import *
from ..logs.log import Log
from ..settings.const import Const

class Window():
    main = None
    f_win = None
    win_key = ''  # window's name
    q_label = None
    k_show_options = None
    levels = {}  # dict of label, min, max, method, is_overridden
    plots = {'x_y': None, 'lambda_y': None, 'lambda_I': None, 'fit_1': None, 'fit_2': None, 'fit_3': None}
    wave_min = 0.  # Angstrom
    wave_max = 0.

    def __init__(self, main, win_key):
        self.main = main
        self.win_key = win_key

    def a_win_info(self,):
        c = Const.colored_text
        ce = Const.end_colored_text
        win_msg = 'Window ' + c + self.win_key + ce + ' details'
        show_message_table(self.win_key, win_msg, self.main.dh.win_info[self.win_key], 700, 700)
