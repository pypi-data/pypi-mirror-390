#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from functools import partial

from ..settings.const import Const
from ..utils.internal_utils import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from ..processing.threads.run_thread import RunThread
from ..logs.log import Log
from ..main.winc import WindowsContainer

class Menu(QFrame):
    main = None # widget windows visualization (main widget)
    c_gradient_theme = None
    c_plot_bg = None
    ks_show_hide = None
    k_link_zoom = None
    q_level_min = None
    q_level_max = None
    i_level_max = None
    i_level_min = None
    c_level_method = None
    c_generate_fit_maps = None
    b_generate_fit_maps = None
    q_generate_fit_maps = None  # label
    q_generate_fit_maps_warning = None
    is_levels_global = True
    s_lambda_rescaling = None
    q_lambda_rescaling = None
    q_abscissa_rescaling = None  # x or t
    q_nb_threads = None
    applied_levels = {'min': None, 'max': None, 'method': None} # float, float, string
    # is either global or local according to user's choice
    is_enabled = None
    q_lambda_min_pc_indicator = None
    q_lambda_max_pc_indicator = None
    q_x_min_pc_indicator = None
    q_x_max_pc_indicator = None
    b_reset_zoom = None
    b_font_size_m = None
    b_font_size_p = None
    font_size_value = Const.default_font_size
    
    def __init__(self, main):
        super(Menu, self).__init__()
        self.setFrameShape(QFrame.StyledPanel)
        self.main = main
        
        l_menu = QVBoxLayout(self)

        # -------- Plots
        self.g_appearance = QGroupBox("Plots")
        #q_appearance_label.setObjectName('box_title')  # create a CSS id (selector # in <file>.css)
        l_grid_plots = QGridLayout(self.g_appearance)

        tooltip_str = 'Change map colors'
        self.q_gradient_label = QLabel('Color map')
        set_tooltip(self.q_gradient_label, tooltip_str)
        self.c_gradient_theme = QComboBox()
        set_tooltip(self.c_gradient_theme, tooltip_str)
        capitalized_themes = list(map(str.capitalize, Const.gradient_themes))
        self.c_gradient_theme.addItems(capitalized_themes)
        self.c_gradient_theme.currentIndexChanged.connect(self.a_updateGradientTheme)
        c_gt_index = self.c_gradient_theme.findText(Const.gradient_default_theme.capitalize(),
                                                    Qt.MatchFixedString)
        if c_gt_index >= 0:
            self.c_gradient_theme.setCurrentIndex(c_gt_index)
        else:
            Log.p('Const.gradient_default_theme does not match with the gradient list.', 'warn')

        tooltip_str = 'Change map background'
        self.q_bg_label = QLabel('Background')
        set_tooltip(self.q_bg_label, tooltip_str)
        self.c_plot_bg = QComboBox()
        set_tooltip(self.c_plot_bg, tooltip_str)
        self.c_plot_bg.addItems(Const.bg_colors.keys())
        self.c_plot_bg.currentIndexChanged.connect(self.a_updatePlotBg)
        c_bg_index = self.c_plot_bg.findText(Const.default_bg_color, Qt.MatchFixedString)
        if c_bg_index >= 0:
            self.c_plot_bg.setCurrentIndex(c_bg_index)
        else:
            Log.p('Const.default_bg_color does not match with the bg_colors list.', 'warn')

        l_grid_plots.addWidget(self.q_gradient_label, 0, 0)
        l_grid_plots.addWidget(self.c_gradient_theme, 0, 1)
        l_grid_plots.addWidget(self.q_bg_label, 1, 0)
        l_grid_plots.addWidget(self.c_plot_bg, 1, 1)

        # -------- Show / Hide plots
        self.g_show_hide = QGroupBox('Show / Hide')
        l_show_hide = QGridLayout(self.g_show_hide)
        
        plot_lists = [  # used for show / hide checkboxes, /!\ LABELS ALSO CHANGED IN menu.py
            ['x_y', 'I(x, y)', True],  # plot_key, title, isChecked
            ['lambda_y', 'I(λ, y)', True],
            ['lambda_I', 'I(λ)', True],
            ['fit_1', 'Fit I(x, y)', False],  # 'Fit (I<sub>0</sub> - I<sub>offset</sub>)(x, y)'
            ['fit_2', 'Fit v(x, y)', False],
            ['fit_3', 'Fit σ(x, y)', False]
        ]

        self.ks_show_hide = {}
        n_line = 0
        n_col = 0
        tooltip_str = 'Check or uncheck to show or hide the related plots'
        for plot_list in plot_lists:
            k_show_hide = QCheckBox(plot_list[1])
            set_tooltip(k_show_hide, tooltip_str)

            k_show_hide.setChecked(plot_list[2])
            k_show_hide.stateChanged.connect(partial(self.a_show_hide, plot_list[0]))

            l_show_hide.addWidget(k_show_hide, n_line, n_col)

            self.ks_show_hide[plot_list[0]] = k_show_hide
            n_col += 1
            if n_col > 2:  # see doc/menu_layout.ods to understand the grid
                n_col = 0
                n_line += 1

        tooltip_str = 'Fit maps generation takes time, you can generate them in background, then check the "Fit..." ' + \
                      'checkboxes to see the result'
        f_generate_fit_maps = QFrame()
        l_generate_fit_maps = QHBoxLayout(f_generate_fit_maps)
        self.b_generate_fit_maps = QPushButton('Generate')
        set_tooltip(self.b_generate_fit_maps, tooltip_str)
        self.q_generate_fit_maps = QLabel('Generate fit maps:')
        set_tooltip(self.q_generate_fit_maps, tooltip_str)
        self.c_generate_fit_maps = QComboBox()
        set_tooltip(self.c_generate_fit_maps, tooltip_str)
        self.c_generate_fit_maps.addItems(['-- Load data first --'])
        self.q_generate_fit_maps_warning = QLabel('')
        self.q_generate_fit_maps_warning.setStyleSheet('color: red;')
        l_generate_fit_maps.addWidget(self.q_generate_fit_maps)
        l_generate_fit_maps.addWidget(self.c_generate_fit_maps)
        l_generate_fit_maps.addWidget(self.b_generate_fit_maps)
        self.b_generate_fit_maps.clicked.connect(self.a_generate_fit_maps)

        l_show_hide.addWidget(f_generate_fit_maps, 2, 0, 1, 3)
        l_show_hide.addWidget(self.q_generate_fit_maps_warning, 3, 0, 1, 3)

        # -------- Levels
        self.g_levels = QGroupBox('Levels')
        l_levels = QGridLayout(self.g_levels)

        f_global_local_levels = QFrame()
        tooltip_str = 'You can either apply level thresholds on all maps or apply these to one specific window by' + \
                      ' choosing the local level option (then change values under the window\'s names)'
        set_tooltip(f_global_local_levels, tooltip_str)
        l_global_local_levels = QHBoxLayout(f_global_local_levels)
        self.r_global_levels = QRadioButton("Global levels")
        self.r_global_levels.setChecked(True)
        self.r_global_levels.toggled.connect(lambda: self.a_global_local_levels(self.r_global_levels))
        l_global_local_levels.addWidget(self.r_global_levels)
        self.r_local_levels = QRadioButton("Local levels (per window)")
        self.r_local_levels.setChecked(False)
        self.r_local_levels.toggled.connect(lambda: self.a_global_local_levels(self.r_local_levels))
        l_global_local_levels.addWidget(self.r_local_levels)

        self.q_level_min = QLabel('Min (%):')
        self.i_level_min = QLineEdit()
        self.i_level_min.setText(Const.default_min)
        self.i_level_min.setFixedWidth(Const.level_input_width)
        self.i_level_min.textChanged.connect(partial(self.a_level_apply, None))
        self.q_level_max = QLabel('Max (%):')
        self.i_level_max = QLineEdit()
        self.i_level_max.setFixedWidth(Const.level_input_width)
        self.i_level_max.setText(Const.default_max)
        self.i_level_max.textChanged.connect(partial(self.a_level_apply, None))
        self.q_level_method = QLabel('Scale:')
        tooltip_str = 'A scale can be applied on the data cube before excluding low and high values according to' + \
            ' the provided percentiles'
        set_tooltip(self.q_level_method, tooltip_str)
        self.c_level_method = QComboBox()
        self.c_level_method.currentIndexChanged.connect(partial(self.a_level_apply, None))
        set_tooltip(self.c_level_method, tooltip_str)
        self.c_level_method.addItems(Const.level_methods)

        self.applied_levels = {'min': float(self.i_level_min.text())}

        l_levels.addWidget(f_global_local_levels, 0, 0, 1, 4)
        l_levels.addWidget(self.q_level_min, 1, 0, 1, 1)
        l_levels.addWidget(self.i_level_min, 1, 1, 1, 1)
        l_levels.addWidget(self.q_level_max, 1, 2, 1, 1)
        l_levels.addWidget(self.i_level_max, 1, 3, 1, 1)
        l_levels.addWidget(self.q_level_method, 2, 0, 1, 1)
        l_levels.addWidget(self.c_level_method, 2, 1, 1, 3)

        # -------- Zoom
        self.g_zoom = QGroupBox('Zoom')
        l_zoom = QVBoxLayout(self.g_zoom)

        self.k_link_zoom = QCheckBox('Link zoom between windows')
        tooltip_str = 'If checked, zoom will be synchronized for all maps between windows'
        set_tooltip(self.k_link_zoom, tooltip_str)
        self.k_link_zoom.stateChanged.connect(self.a_link_zoom)

        self.b_reset_zoom = QPushButton('Reset zoom')
        tooltip_str = 'Reset zoom of the maps'
        set_tooltip(self.b_reset_zoom, tooltip_str)
        self.b_reset_zoom.clicked.connect(self.a_reset_zoom)

        self.q_nb_threads = QLabel('')  # Updated by main.update_nb_threads()
        tooltip_str = 'You can see here how many processes run in background'
        set_tooltip(self.q_nb_threads, tooltip_str)
        self.main.update_thread_text(self.q_nb_threads)

        f_lambda_rescaling = QFrame()
        tooltip_str = 'Rescale the abscissa of the second map I(lambda, y)'
        set_tooltip(f_lambda_rescaling, tooltip_str)
        l_lambda_rescaling = QHBoxLayout(f_lambda_rescaling)
        self.s_lambda_rescaling = QSlider(Qt.Horizontal)
        self.s_lambda_rescaling.setMinimum(1)  # scale = 1
        self.s_lambda_rescaling.setMaximum(Const.max_lambda_rescaling)
        self.s_lambda_rescaling.setValue(Const.default_lambda_rescaling)
        self.s_lambda_rescaling.valueChanged.connect(self.a_lambda_rescaling)
        self.q_lambda_rescaling_title = QLabel(Const.lambda_char + ' rescaling: ')
        l_lambda_rescaling.addWidget(self.q_lambda_rescaling_title)
        self.q_lambda_rescaling = QLabel('')  # updated by update_lambda_rescaling_label()
        self.update_lambda_rescaling_label()
        l_lambda_rescaling.addWidget(self.q_lambda_rescaling)
        self.q_lambda_min_pc_indicator = QLabel(' x1')
        l_lambda_rescaling.addWidget(self.q_lambda_min_pc_indicator)
        l_lambda_rescaling.addWidget(self.s_lambda_rescaling)
        self.q_lambda_max_pc_indicator = QLabel('x' + str(Const.max_lambda_rescaling))
        l_lambda_rescaling.addWidget(self.q_lambda_max_pc_indicator)

        f_x_rescaling = QFrame()
        tooltip_str = 'Rescale the abscissa of the first map I(x, y)'
        set_tooltip(f_x_rescaling, tooltip_str)
        l_x_rescaling = QHBoxLayout(f_x_rescaling)
        self.s_x_rescaling = QSlider(Qt.Horizontal)
        self.s_x_rescaling.setMinimum(1)  # scale = 1
        self.s_x_rescaling.setMaximum(Const.max_x_rescaling)
        self.s_x_rescaling.setValue(Const.default_x_rescaling)
        self.s_x_rescaling.valueChanged.connect(partial(self.a_x_rescaling, None))
        self.q_abscissa_rescaling = QLabel('x rescaling: ')
        l_x_rescaling.addWidget(self.q_abscissa_rescaling)
        self.q_x_rescaling = QLabel('')  # updated by update_x_rescaling_label()
        self.update_x_rescaling_label()
        l_x_rescaling.addWidget(self.q_x_rescaling)
        self.q_x_min_pc_indicator = QLabel(' x1')
        l_x_rescaling.addWidget(self.q_x_min_pc_indicator)
        l_x_rescaling.addWidget(self.s_x_rescaling)
        self.q_x_max_pc_indicator = QLabel('x' + str(Const.max_x_rescaling))
        l_x_rescaling.addWidget(self.q_x_max_pc_indicator)

        f_plot_size = QFrame()
        l_plot_size = QHBoxLayout(f_plot_size)
        self.main.s_plot_size = QSlider(Qt.Horizontal)
        self.main.s_plot_size.setMinimum(Const.min_plot_size)
        self.main.s_plot_size.setMaximum(Const.max_plot_size)
        self.main.s_plot_size.setValue(Const.default_plot_size)
        self.main.s_plot_size.valueChanged.connect(self.a_plot_size)
        self.q_plot_sizes = QLabel('Plot sizes: ')
        l_plot_size.addWidget(self.q_plot_sizes)
        self.q_plot_size = QLabel('')  # updated by update_plot_size_label()
        self.update_plot_size_label()
        l_plot_size.addWidget(self.q_plot_size)
        l_plot_size.addWidget(QLabel(str(Const.min_plot_size_pc) + ' %'))
        l_plot_size.addWidget(self.main.s_plot_size)
        l_plot_size.addWidget(QLabel(str(Const.max_plot_size_pc) + ' %'))

        f_font_size = QFrame()
        l_font_size = QHBoxLayout(f_font_size)
        self.font_size_value = Const.default_font_size
        self.b_font_size_m = QPushButton('-')
        self.b_font_size_m.clicked.connect(partial(self.a_font_size, '-'))
        self.b_font_size_p = QPushButton('+')
        self.b_font_size_p.clicked.connect(partial(self.a_font_size, '+'))
        self.q_font_size_title = QLabel('Text font size: ')
        l_font_size.addWidget(self.q_font_size_title)
        self.q_font_size = QLabel('')  # updated by update_font_size_label()
        self.q_font_size.setAlignment(Qt.AlignCenter)
        self.update_font_size_label()
        self.q_font_size_min_indicator = QLabel(str(Const.min_font_size_pc) + ' %')
        l_font_size.addWidget(self.q_font_size_min_indicator)
        l_font_size.addWidget(self.b_font_size_m)
        l_font_size.addWidget(self.q_font_size)
        l_font_size.addWidget(self.b_font_size_p)
        self.q_font_size_max_indicator = QLabel(str(Const.max_font_size_pc) + ' %')
        l_font_size.addWidget(self.q_font_size_max_indicator)

        l_zoom.addWidget(self.b_reset_zoom)
        l_zoom.addWidget(self.k_link_zoom)
        l_zoom.addWidget(f_x_rescaling)
        l_zoom.addWidget(f_lambda_rescaling)
        l_zoom.addWidget(f_plot_size)
        l_zoom.addWidget(f_font_size)

        l_menu.addWidget(self.g_appearance)
        l_menu.addWidget(self.g_show_hide)
        l_menu.addWidget(self.g_levels)
        l_menu.addWidget(self.g_zoom)
        l_menu.addWidget(self.q_nb_threads)
        l_menu.stretch(1)

        self.disable()

    def a_reset_zoom(self):
        for plot in self.main.all_plots():
            if plot.plot_key == 'x_y' or 'fit' in plot.plot_key:
                plot.main_plot_item.autoRange()

    def enable(self):
        self.enable_disable(True)

    def disable(self):
        self.enable_disable(False)

    def enable_disable(self, enable):  # usage: use menu.enable() or menu.disable() instead
        if self.is_enabled != enable:  # otherwise already good state
            self.g_appearance.setEnabled(enable)
            self.g_show_hide.setEnabled(enable)
            if self.main.dh is not None:
                self.ks_show_hide['x_y'].setEnabled(not self.main.dh.is_full_spectrum)
                self.ks_show_hide['fit_1'].setEnabled(not self.main.dh.is_full_spectrum)
                self.ks_show_hide['fit_2'].setEnabled(not self.main.dh.is_full_spectrum)
                self.ks_show_hide['fit_3'].setEnabled(not self.main.dh.is_full_spectrum)
                self.c_generate_fit_maps.setEnabled(not self.main.dh.is_full_spectrum)
                self.b_generate_fit_maps.setEnabled(not self.main.dh.is_full_spectrum)
                self.q_generate_fit_maps.setEnabled(not self.main.dh.is_full_spectrum)
                warning = ''
                if self.main.dh.is_full_spectrum:
                    warning = 'I(x,y) and fit maps are disabled for single exposure.'
                self.q_generate_fit_maps_warning.setText(warning)
            self.g_levels.setEnabled(enable)
            self.g_zoom.setEnabled(enable)
            self.is_enabled = enable

    def prepare_levels(self, win_key=False):
        try:
            if win_key is not False:  # local levels
                w = self.main.get_window(win_key)
                min_ = float(w.levels['min'].text())  # %
                max_ = float(w.levels['max'].text())  # %
                method = w.levels['method'].currentText()
            else:  # global levels
                min_ = float(self.i_level_min.text())  # %
                max_ = float(self.i_level_max.text())  # %
                method = self.c_level_method.currentText()
        except ValueError:  # not float => abort process
            return False

        if (0 <= min_ <= 100) and \
           (0 <= max_ <= 100) and \
           (max_ > min_):
            self.applied_levels['min'] = min_
            self.applied_levels['max'] = max_
            self.applied_levels['method'] = method
            return True
        return False

    def a_global_local_levels(self, button):
        if button.text() == 'Global levels':  # triggered whether Local or Global is checked
            self.is_levels_global = button.isChecked()  # Global is checked
            css_label_local = Const.label_disabled if self.is_levels_global else Const.label_enabled
            css_label_global = Const.label_enabled if self.is_levels_global else Const.label_disabled

            self.q_level_min.setStyleSheet(css_label_global)
            self.q_level_max.setStyleSheet(css_label_global)

            self.i_level_min.setEnabled(self.is_levels_global)
            self.i_level_max.setEnabled(self.is_levels_global)

            self.q_level_method.setStyleSheet(css_label_global)
            self.c_level_method.setEnabled(self.is_levels_global)

            for w in self.main.windows:
                # Synchronize local and global
                try:
                    w.levels['min'].textChanged.disconnect()  # avoid trigger useless threads
                    w.levels['max'].textChanged.disconnect()
                    w.levels['method'].currentIndexChanged.disconnect()
                except TypeError:  # do not happen (when no previous connection exists)
                    pass

                w.levels['min'].setText(self.i_level_min.text())
                w.levels['max'].setText(self.i_level_max.text())
                w.levels['method'].setCurrentIndex(self.c_level_method.currentIndex())

                w.levels['label'].setStyleSheet(css_label_local)
                w.levels['min'].setEnabled(not self.is_levels_global)
                w.levels['max'].setEnabled(not self.is_levels_global)
                w.levels['method'].setEnabled(not self.is_levels_global)

                w.levels['min'].textChanged.connect(partial(self.a_level_apply, w))  # reconnecting threads
                w.levels['max'].textChanged.connect(partial(self.a_level_apply, w))
                w.levels['method'].currentIndexChanged.connect(partial(self.a_level_apply, w))

            if self.is_levels_global:  # potentially user changed local levels somewhere
                self.a_level_apply()

    def a_plot_size(self):
        for plot in self.main.all_plots():
            if self.main.f_menu.ks_show_hide[plot.plot_key].isChecked():
                plot.setSize()
                if plot.plot_key == 'x_y':
                    plot.main_plot_item.autoRange()  # View all
        self.update_plot_size_label()

    def a_font_size(self, m_or_p):
        if m_or_p == '+':  # bigger
            self.font_size_value += 1
            if self.font_size_value > Const.max_font_size:
                self.font_size_value = Const.max_font_size
        else:  # - smaller
            self.font_size_value -= 1
            if self.font_size_value < Const.min_font_size:
                self.font_size_value = Const.min_font_size
        labels = [self.g_appearance, self.q_gradient_label,
            self.q_bg_label,
            self.g_show_hide,
            self.b_generate_fit_maps,
            self.q_generate_fit_maps,
            self.c_generate_fit_maps,
            self.q_generate_fit_maps_warning,
            self.g_levels,
            self.r_global_levels,
            self.r_local_levels,
            self.q_level_min,
            self.q_level_max,
            self.q_level_method,
            self.c_level_method,
            self.g_zoom,
            self.b_reset_zoom,
            self.q_nb_threads,
            self.q_lambda_rescaling,
            self.q_abscissa_rescaling,
            self.q_x_rescaling,
            self.q_lambda_min_pc_indicator,
            self.q_lambda_max_pc_indicator,
            self.q_x_min_pc_indicator,
            self.q_x_max_pc_indicator,
            self.c_generate_fit_maps,
            self.c_gradient_theme,
            self.c_plot_bg,
            self.i_level_min,
            self.i_level_max,
            self.q_lambda_rescaling_title,
            self.q_plot_sizes,
            self.b_font_size_m,
            self.b_font_size_p,
            self.k_link_zoom,
            self.q_font_size_title,
            self.q_font_size,
            self.q_font_size_min_indicator,
            self.q_font_size_max_indicator
        ]
        labels += self.ks_show_hide.values()
        setFontSizes(labels, self.font_size_value)
        self.update_font_size_label()
        
    def update_plot_size_label(self):
        plot_size = self.main.s_plot_size.value()

        # ax + b, pixels to % according to the settings
        a = (Const.max_plot_size_pc - Const.min_plot_size_pc) / (Const.max_plot_size - Const.min_plot_size)
        b = Const.min_plot_size_pc - a * Const.min_plot_size
        plot_size_pc = int(a * plot_size + b)

        self.q_plot_size.setText('<font color="' + Const.green_text +
                                 '">' + str(plot_size_pc) + ' %')

    def update_font_size_label(self):
        # ax + b, pixels to % according to the settings
        a = (Const.max_font_size_pc - Const.min_font_size_pc) / (Const.max_font_size - Const.min_font_size)
        b = Const.min_font_size_pc - a * Const.min_font_size
        font_size_pc = int(a * self.font_size_value + b)

        self.q_font_size.setText('<font color="' + Const.green_text +
                                 '">' + str(font_size_pc) + ' %')

    def update_generate_list(self):
        self.c_generate_fit_maps.clear()
        self.c_generate_fit_maps.addItems(['All windows (will take time)'] + self.main.dh.data_info['win_keys'])
        self.c_generate_fit_maps.setCurrentIndex(1)  # first window
        # default selected is updated when fit maps bars move
    
    def a_link_zoom(self):
        self.main.link_axes(self.k_link_zoom.isChecked())
        
    def update_x_rescaling_label(self):
        self.q_x_rescaling.setText('<font color="' + Const.green_text +
                                        '">x' + str(self.s_x_rescaling.value()) + '</font>')

    def update_lambda_rescaling_label(self):
        self.q_lambda_rescaling.setText('<font color="' + Const.green_text +
                                        '">x' + str(self.s_lambda_rescaling.value()) + '</font>')

    def a_x_rescaling(self, specific_win_key=None):  # None means all windows
        scale = self.main.abscissa_factor('x_y')
        self.update_x_rescaling_label()
        for win_key, plot_bloc in self.main.global_plots.items():
            if specific_win_key is None or specific_win_key == win_key:
                plots_to_update = ['x_y', 'fit_1', 'fit_2', 'fit_3']
                for plot_key in plots_to_update:
                    plot_bloc[plot_key].apply_transform()
                    if plot_bloc[plot_key].vertical_bar is not None:  # bar not ready yet
                        plot_bloc[plot_key].vertical_bar.setBounds(([0, self.main.dh.get_adjusted_third_D(
                                                                    plot_bloc[plot_key])]))
                    #plot_bloc[plot_key].updateLimits(scale, 1)
                self.main.update_vertical_bar(plot_bloc)

    def a_lambda_rescaling(self):  # None means all windows
        self.update_lambda_rescaling_label()
        for win_key, plot_bloc in self.main.global_plots.items():
            plot_bloc['lambda_y'].apply_transform()
            if plot_bloc['lambda_y'].vertical_bar is not None:  # bar not ready yet
                len_ = self.main.dh.get_adjusted_third_D(plot_bloc['lambda_y'])
                plot_bloc['lambda_y'].vertical_bar.setBounds(([0, len_]))
                self.main.update_vertical_bar(plot_bloc)
                #plot_bloc['lambda_y'].updateLimits(scale, 1)

    @staticmethod
    def remove_updating_levels(rt):
        if rt in rt.main.updating_levels:
            rt.main.updating_levels.remove(rt)


    def a_level_apply(self, w=None):
        if self.main.dh is not None:  # data have been loaded
            if w is None or w is False:  # global levels
                use_win_key = False
            else:  # local levels
                use_win_key = w.win_key
            if not self.prepare_levels(use_win_key):  # not float
                return
            global_local_str = 'Global' if self.is_levels_global else 'Local'
            thread_name = 'Applying ' + str(global_local_str) + ' levels ' + str(self.applied_levels['min']) + ' % to ' + \
                          str(self.applied_levels['max']) + ' % (' + self.applied_levels['method'] + ')'

            for previous_running_rt in self.main.updating_levels:
                previous_running_rt.interrupt()
            rt = RunThread('UpdateLevels', self.main, use_win_key, thread_name, self.remove_updating_levels)
            self.main.updating_levels.append(rt)

    @staticmethod
    def end_fit_maps(rt):
        plot_bloc = rt.end_func_args
        win_key = plot_bloc['x_y'].w.win_key
        Menu.enable_fit_generation(rt)
        fit_maps_checked = []
        for i in range(3):
            key = 'fit_' + str(i + 1)
            if rt.main.f_menu.ks_show_hide[key].isChecked():
                fit_maps_checked.append(rt.main.global_plots[win_key][key])
        if not rt.running_thread.do_interrupt:
            rt.main.fit_maps_are_generated[win_key] = True

            if len(fit_maps_checked) > 0:
                for fit_map in fit_maps_checked:
                    fit_map.show_hide(True)
            else:
                show_message('Fit maps info', 'Fit maps have been generated, check the "Fit [...]" checkboxes'
                         ' in the left menu in order to see them (will be below I(' + rt.main.dh.x_or_t
                         + ',y), I(λ, y) and I(λ) plots)')

        for i in range(1, 4):
            plot_bloc['fit_' + str(i)].setup_horizontal_bars()
            plot_bloc['fit_' + str(i)].setup_vertical_bars()
            plot_bloc['fit_' + str(i)].viewAll()
        rt.main.update_vertical_bar(plot_bloc)

    @staticmethod
    def enable_fit_generation(rt):
        win_key = rt.end_func_args['x_y'].w.win_key
        rt.main.fit_maps_are_generating[win_key] = False

    def a_generate_fit_maps(self):
        if self.main.dh is None:  # no data loaded yet
            show_message('Fit maps warning', 'Load a data file first.')
        else:
            are_generating = self.main.fit_maps_are_generating
            win_key = self.c_generate_fit_maps.currentText()
            win_keys = self.main.dh.data_info['win_keys']
            all_windows = win_key not in win_keys  # user selected 'Generate all windows'
            
            if (win_key in are_generating and are_generating[win_key]) or \
                    (
                     all_windows and len(are_generating) == len(win_keys) and
                     list(are_generating.values()).count(True) == len(are_generating)
                    ):  # It means all windows were generated
                show_message('Fit maps warning', 'You already run the fit maps generation for this(these) window(s).')
            else:
                window_keys = win_keys if all_windows else [win_key]

                for win_key, plot_bloc in self.main.global_plots.items():
                    if (win_key not in are_generating or are_generating[win_key] is False) and \
                            win_key in window_keys:
                        xy_map = plot_bloc['x_y']
                        y_range_str = '[' + str(xy_map.fit_maps_y_min) + '; ' + str(xy_map.fit_maps_y_max) + ']'
                        qm = QMessageBox()
                        ret = qm.Yes
                        if not self.main.is_generate_maps_warned:
                            self.main.is_generate_maps_warned = True
                            ret = qm.question(self, '',  'Before generating fit maps, you can adjust the y bounds in order ' +
                                              'to aim a specific region and save time, use the grey horizontal bars in I(' + self.main.dh.x_or_t + ',y) maps. ' +
                                              '\nGenerate fit maps with current y bounds anyway?', qm.Yes | qm.No)
                        if ret == qm.Yes:
                            self.main.fit_maps_are_generating[win_key] = True
                            RunThread('GenerateFitMaps', self.main, plot_bloc,
                                      'Generating ' + str(xy_map.w.win_key) + '\'s fit maps, y ∈ ' + y_range_str,
                                      Menu.end_fit_maps, plot_bloc)
        
    def a_show_hide(self, plot_key=None):
        if self.main.are_data_loaded:
            for plot in self.main.all_plots():
                if plot.plot_key == plot_key or plot_key is None:
                    plot.show_hide(self.ks_show_hide[plot.plot_key].isChecked())
                    if 'fit' in plot.plot_key:
                        plot.viewAll()
                    
    def a_updatePlotBg(self, i):
        plot_bg = Const.bg_colors[self.c_plot_bg.itemText(i)]
        for plot in self.main.all_plots():
            plot.setPlotBackground(plot_bg)
        
    def a_updateGradientTheme(self, i):
        for plot in self.main.all_plots():
            if isClassName(plot, 'PlotMap'):
                plot.iv.setPredefinedGradient(self.c_gradient_theme.itemText(i).lower())
                plot.hide_level_ticks()
