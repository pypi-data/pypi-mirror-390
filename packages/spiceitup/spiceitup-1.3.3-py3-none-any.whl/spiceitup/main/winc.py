#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from functools import partial

from ..processing.threads.run_thread import RunThread
from ..main.w import Window
import time
from ..settings.const import Const
from ..utils.internal_utils import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from ..layout.flow_layout import FlowLayout
#from pylab import *
import pyqtgraph as pg
from ..plot.plot_map import PlotMap
from ..plot.plot_line import PlotLine
from ..toolbox.clickable_qlabel import ClickableQLabel
from ..logs.log import Log


class WindowsContainer(QFrame):
    main = None  # widget windows visualization (main widget)
    vbox = None
    l_flow = None
    f_plots = None
    q_win_text = None
    fit_labels = {}
    first_time_ms = 0
    
    def __init__(self, main):
        super(WindowsContainer, self).__init__()
        self.setFrameShape(QFrame.StyledPanel)
        self.main = main
        self.vbox = QVBoxLayout(self)
        self.f_plots = QFrame()
        
        w_scroll = QScrollArea()
        w_scroll.setWidget(self.f_plots)
        w_scroll.setWidgetResizable(True)
        self.vbox.addWidget(w_scroll)
        
        self.init_display()

    def reset_display_parameters(self):
        self.main.are_data_loaded = False
        for w in self.main.windows:
            w.f_win.deleteLater()
        self.main.windows = []
        self.main.global_plots = {}
        self.main.f_footer.interrupt_processes()
        for th in self.main.ths:
            th.do_interrupt = True
        """for th in self.main.ths:
            try:
                th.quit()
                th.deleteLater()
            except RuntimeError:  # thread was already deleted
                pass
        for thw in self.main.thws:
            try:
                thw.deleteLater()
            except RuntimeError:  # thread worker was already deleted
                pass
        self.main.ths = []
        self.main.thws = []"""
        self.main.update_nb_threads(0)
        self.main.fit_maps_are_generating = {}
        self.main.fit_maps_are_generated = {}
        self.main.double_click = False
        self.main.updating_profile = {}
        self.main.force_third_D = False
        self.main.force_lambda_bar = False
        self.main.qs_fit_label = {}
        self.main.nb_available_bin = {}

        self.main.f_menu.s_x_rescaling.setValue(Const.default_x_rescaling)
        self.main.f_menu.s_lambda_rescaling.setValue(Const.default_lambda_rescaling) # needed for updateLimits behavior

    def init_display(self):
        self.l_flow = FlowLayout()
        self.q_win_text = QLabel('No data yet')
        self.l_flow.addWidget(self.q_win_text)
        self.f_plots.setLayout(self.l_flow)
    
    def a_horizontal_bar_moved(self, bar, plot_map, force=False):
        if force:
            self.main.force_third_D = True
        for win_key, plot_bloc in self.main.global_plots.items():
            val = bar.value()
            plots = [plot_bloc['x_y'], plot_bloc['lambda_y'], plot_bloc['fit_1'], plot_bloc['fit_2'], plot_bloc['fit_3']]
            for plot in plots:
                if plot != plot_map and plot.horizontal_bar is not None:
                    plot.horizontal_bar.setValue(val)
            plot_bloc['lambda_I'].updatePlotData()
        if force:
            RunThread('MakeProcessAvailable', self.main, {'process': 'force_third_D',
                                                          'rate': Const.restore_force_third_D})

    def a_vertical_bar_moved(self, bar, plot_map, force=False):
        if force:
            self.main.force_third_D = True
        if plot_map.plot_key == 'x_y' or 'fit' in plot_map.plot_key:
            other_plot_key = 'lambda_y'
        else:
            other_plot_key = 'x_y'
        plot_bloc = self.main.get_plot_bloc(plot_map)
        adjusted_value = int(round(bar.value() / self.main.abscissa_factor(plot_map.plot_key)))
        plot_bloc[other_plot_key].set_third_D_value(adjusted_value)
        if force:
            if plot_map.plot_key == 'x_y' or 'fit' in plot_map.plot_key:
                time.sleep(Const.thread_rate)  # don't take into account last slider movement
                for win_key, plot_bloc in self.main.global_plots.items():
                    plot_bloc['lambda_I'].updatePlotData()
            RunThread('MakeProcessAvailable', self.main, {'process': 'force_third_D',
                                                          'rate': Const.restore_force_third_D})

    def fit_maps_bar_moved(self, xy_map):
        bar_val_1 = round(xy_map.fit_maps_bar_min.value())
        bar_val_2 = round(xy_map.fit_maps_bar_max.value())
        xy_map.fit_maps_y_min = bar_val_1
        xy_map.fit_maps_y_max = bar_val_2
        if bar_val_1 > bar_val_2:
            xy_map.fit_maps_y_min = bar_val_2
            xy_map.fit_maps_y_max = bar_val_1
        self.main.f_menu.c_generate_fit_maps.setCurrentText(xy_map.w.win_key)

        if not self.main.are_grey_bars_warned:
            y_bounds = self.main.dh.y_fit_bounds[xy_map.w.win_key]
            show_message('Warning', 'These red bars are used to restrict the ROI used to generate the fit maps '
                         '(e.g. to ignore dumbbells).<br /><br />' +
                         '- Initial default range was: y ∈ [' + str(y_bounds[0]) +
                         '; ' + str(y_bounds[1]) + ']<br />' +
                         '- It is now: y ∈ [' + str(xy_map.fit_maps_y_min) + '; ' +
                         str(xy_map.fit_maps_y_max) + ']'
                         )
            self.main.is_generate_maps_warned = True
            self.main.are_grey_bars_warned = True


    def generateOneWindow(self, win_key, generateWindows_rt):  # i.e. 2 maps, 1 plot (+3 fit maps)
        #Log.p_ms('generateOneWindow ' + str(win_key), self.first_time_ms)
        w = Window(self.main, win_key)
        w.f_win = QFrame()
        l_grid = QGridLayout(w.f_win)
        
        f_win_header = QFrame()
        l_win_header = QGridLayout(f_win_header) # includes local levels
        w.q_label = QLabel(win_key)
        w.q_label.setFont(Const.css_window_font)

        img_i = ClickableQLabel()
        tooltip_str = 'See window and study details'
        set_tooltip(img_i, tooltip_str)
        img_i.setPixmap(QPixmap('images/info.png'))
        img_i.clicked.connect(lambda: w.a_win_info())
        
        # ----- Levels per window
        i_level_min = QLineEdit()
        i_level_min.setFixedWidth(Const.level_input_width)
        i_level_min.setText(Const.default_min)
        i_level_min.setEnabled(False)
        i_level_min.textChanged.connect(partial(self.main.f_menu.a_level_apply, w))

        i_level_max = QLineEdit()
        i_level_max.setFixedWidth(Const.level_input_width)
        i_level_max.setText(Const.default_max)
        i_level_max.setEnabled(False)
        i_level_max.textChanged.connect(partial(self.main.f_menu.a_level_apply, w))

        c_level_method = QComboBox()
        tooltip_str = 'A scale can be applied on the data cube before excluding low and high values according to' + \
                      ' the provided percentiles'
        set_tooltip(c_level_method, tooltip_str)
        c_level_method.addItems(Const.level_methods)
        c_level_method.setEnabled(False)
        c_level_method.currentIndexChanged.connect(partial(self.main.f_menu.a_level_apply, w))
        q_levels = QLabel('Levels (%)')
        q_levels.setStyleSheet(Const.label_disabled)
        w.levels = {'label': q_levels, 'min': i_level_min,
            'max': i_level_max, 'method': c_level_method, 'is_overridden': False}
        self.main.f_menu.prepare_levels()

        l_win_header.addWidget(img_i, 0, 0, 1, 1)
        l_win_header.addWidget(w.q_label, 0, 1, 1, 3)

        l_win_header.addWidget(q_levels, 1, 0, 1, 1)
        l_win_header.addWidget(i_level_min, 1, 1, 1, 1)
        l_win_header.addWidget(i_level_max, 1, 2, 1, 1)
        l_win_header.addWidget(c_level_method, 1, 3, 1, 1)
        l_win_header.setColumnStretch(4, 1)
        
        # ----- Plot 1
        q_x_y_label = QLabel('I(' + self.main.dh.x_or_t + ', y) ' + self.main.dh.I_unit)
        tooltip_str = 'This is the I(' + self.main.dh.x_or_t + ', y) map, values in blue match the mouse position'
        set_tooltip(q_x_y_label, tooltip_str)
        q_x_y_label.setFont(Const.css_plot_font)
        q_x_y_label.setStyleSheet(Const.css_borders + ' ' + Const.css_plot_title)
        q_x_y_label.setAlignment(Qt.AlignCenter)
        f_bottom_plot1 = QFrame()
        l_bottom_plot1 = QVBoxLayout(f_bottom_plot1)
        q_label_lambda = QLabel('')  # updated in PlotMap()
        q_label_lambda.setStyleSheet('color: ' + Const.slider_cursor_color + ';')
        q_label_lambda.setAlignment(Qt.AlignCenter)
        l_bottom_plot1.addWidget(q_label_lambda)
        
        f_x_y_options = QFrame()
        l_x_y_options = QGridLayout(f_x_y_options)
        q_ave_1d_label = QLabel('Ave. 1D over ' + Const.lambda_char + ':')
        tooltip_str = 'Maps will be averaged together over the lambda dimension'
        set_tooltip(q_ave_1d_label, tooltip_str)
        l_x_y_options.addWidget(q_ave_1d_label, 0, 0)
        c_x_y_average1D = QComboBox()
        set_tooltip(c_x_y_average1D, tooltip_str)
        c_x_y_average2D = QComboBox()

        #Log.p_ms('x_y...', self.first_time_ms)
        w.plots['x_y'] = PlotMap(w, self.main, 'x_y', q_x_y_label, q_label_lambda,
                                 f_bottom_plot1, f_x_y_options, c_x_y_average1D,
                                 c_x_y_average2D, generateWindows_rt)
        b_export_x_y = QPushButton('Export')
        b_export_x_y.clicked.connect(w.plots['x_y'].export)
        #Log.p_ms('x_y done.', self.first_time_ms)

        average_values = self.main.dh.average1D_values(w.plots['x_y'], 'lambda')
        c_x_y_average1D.addItems(average_values)
        c_x_y_average1D.currentIndexChanged.connect(w.plots['x_y'].a_average1D)
        l_x_y_options.addWidget(c_x_y_average1D, 0, 1)
        b_whole_dim = QPushButton('Whole dim.')
        tooltip_str = 'All maps will be averaged over the lambda dimension in order to have one I(' + \
                      self.main.dh.x_or_t + ', y) map'
        set_tooltip(b_whole_dim, tooltip_str)
        b_whole_dim.clicked.connect(partial(w.plots['x_y'].a_average_whole_dim, c_x_y_average1D, len(average_values) - 1))
        l_x_y_options.addWidget(b_whole_dim, 0, 2)

        q_ave_2d_label = QLabel('Smooth 2D (' + self.main.dh.x_or_t + ', y):')
        tooltip_str = 'Maps will be averaged in the map dimension itself, i.e. in (' + self.main.dh.x_or_t + ', y).' + \
            ' This is performed thanks to opencv.filter2D'
        set_tooltip(q_ave_2d_label, tooltip_str)
        set_tooltip(c_x_y_average2D, tooltip_str)
        l_x_y_options.addWidget(q_ave_2d_label, 1, 0)
        c_x_y_average2D.addItems(Const.average2D_choices)
        c_x_y_average2D.currentIndexChanged.connect(w.plots['x_y'].a_average2D)
        l_x_y_options.addWidget(c_x_y_average2D, 1, 1)

        #l_x_y_options.addWidget(b_export_x_y, 1, 2)
        l_x_y_options.addWidget(QFrame(), 1, 2)
        
        # ----- Plot 2
        q_lambda_y_label = QLabel('I(' + Const.lambda_char + ', y) ' + self.main.dh.I_unit)
        tooltip_str = 'This is the I(lambda, y) map, values in blue match the mouse position'
        set_tooltip(q_lambda_y_label, tooltip_str)
        q_lambda_y_label.setFont(Const.css_plot_font)
        q_lambda_y_label.setStyleSheet(Const.css_borders + ' ' + Const.css_plot_title)
        q_lambda_y_label.setAlignment(Qt.AlignCenter)
        f_bottom_plot2 = QFrame()
        l_bottom_plot2 = QVBoxLayout(f_bottom_plot2)
        q_label_x = QLabel('')  # updated in PlotMap()
        q_label_x.setStyleSheet('color: ' + Const.slider_cursor_color + ';')
        q_label_x.setAlignment(Qt.AlignCenter)
        l_bottom_plot2.addWidget(q_label_x)
        
        f_lambda_y_options = QFrame()
        l_lambda_y_options = QGridLayout(f_lambda_y_options)
        q_ave_1d_label = QLabel('Ave. 1D over ' + self.main.dh.x_or_t + ':')
        tooltip_str = 'Maps will be averaged together over the ' + self.main.dh.x_or_t + ' dimension'
        set_tooltip(q_ave_1d_label, tooltip_str)
        l_lambda_y_options.addWidget(q_ave_1d_label, 0, 0)
        c_lambda_y_average1D = QComboBox()
        set_tooltip(c_lambda_y_average1D, tooltip_str)
        c_lambda_y_average2D = QComboBox()
        #Log.p_ms('l_y...', self.first_time_ms)
        w.plots['lambda_y'] = PlotMap(w, self.main, 'lambda_y', q_lambda_y_label,
                                      q_label_x, f_bottom_plot2, f_lambda_y_options,
                                      c_lambda_y_average1D, c_lambda_y_average2D, generateWindows_rt)
        #Log.p_ms('l_done...', self.first_time_ms)

        b_export_lambda_y = QPushButton('Export')
        b_export_lambda_y.clicked.connect(w.plots['lambda_y'].export)

        average_values = self.main.dh.average1D_values(w.plots['lambda_y'], self.main.dh.x_or_t)
        c_lambda_y_average1D.addItems(average_values)
        c_lambda_y_average1D.currentIndexChanged.connect(w.plots['lambda_y'].a_average1D)
        l_lambda_y_options.addWidget(c_lambda_y_average1D, 0, 1)
        b_whole_dim = QPushButton('Whole dim.')
        tooltip_str = 'All maps will be averaged over the ' + self.main.dh.x_or_t + ' dimension in order to have one I(' + \
                      'lambda, y) map'
        set_tooltip(b_whole_dim, tooltip_str)
        b_whole_dim.clicked.connect(partial(w.plots['lambda_y'].a_average_whole_dim, c_lambda_y_average1D, len(average_values) - 1))
        l_lambda_y_options.addWidget(b_whole_dim, 0, 2)
        q_ave_2d_label = QLabel('Smooth 2D (' + Const.lambda_char + ', y):')
        tooltip_str = 'Maps will be averaged in the map dimension itself, i.e. in (lambda, y). ' + \
                      'This is performed thanks to opencv.filter2D'
        set_tooltip(q_ave_2d_label, tooltip_str)
        set_tooltip(c_lambda_y_average2D, tooltip_str)
        l_lambda_y_options.addWidget(q_ave_2d_label, 1, 0)
        c_lambda_y_average2D.addItems(Const.average2D_choices)
        c_lambda_y_average2D.currentIndexChanged.connect(w.plots['lambda_y'].a_average2D)
        l_lambda_y_options.addWidget(c_lambda_y_average2D, 1, 1)
        #l_lambda_y_options.addWidget(b_export_lambda_y, 1, 2)
        l_lambda_y_options.addWidget(QFrame(), 1, 2)
        
        # ----- Plot 3
        q_lambda_I_label = QLabel('')  # updated in UpdateProfile()
        tooltip_str = 'This is the I(lambda) histogram, it\'s computed according to the blue cross positions in the' + \
                      ' previous maps, related values of ' + self.main.dh.x_or_t + ' and y are displayed in green here'
        set_tooltip(q_lambda_I_label, tooltip_str)
        q_lambda_I_label.setAlignment(Qt.AlignCenter)
        q_lambda_I_label.setFont(Const.css_plot_font)
        q_lambda_I_label.setStyleSheet('color: ' + Const.green_text +
                                       '; ' + Const.css_borders + ' ' + Const.css_plot_title)
        
        q_lambda_I_title = QLabel('')  # below plot, updated in get_gaussian_fit()
        tooltip_str = 'Gaussian formula used to compute the fit'
        set_tooltip(q_lambda_I_title, tooltip_str)
        q_lambda_I_title.setAlignment(Qt.AlignCenter)
        q_lambda_I_title.setStyleSheet('color: white;')
        q_fit_label = QLabel('')  # updated in PlotLine()
        tooltip_str = 'Gaussian fit parameters that are retrieved'
        set_tooltip(q_fit_label, tooltip_str)
        q_fit_label.setAlignment(Qt.AlignCenter)
        q_fit_label.setStyleSheet('color: ' + Const.fit_text_color + ';')
        
        x_index = round(self.main.dh.get_dim(win_key, self.main.dh.x_or_t) / 2.)
        #Log.p_ms('profile...', self.first_time_ms)
        w.plots['lambda_I'] = PlotLine(w, self.main, 'lambda_I', x_index,
                                       q_lambda_I_label, q_fit_label, q_lambda_I_title)
        #Log.p_ms('profile done.', self.first_time_ms)

        self.fit_labels = {'fit_1': 'Fit: I<sub>max</sub>(' + self.main.dh.x_or_t + ', y)',
                           'fit_2': 'Fit: v(' + self.main.dh.x_or_t + ', y)',
                           'fit_3': 'Fit: ' + Const.sigma_char + '(' + self.main.dh.x_or_t + ', y)'}
            
        # ----- Fit Map 1 (I_max)
        q_fit_1_label = QLabel(self.fit_labels['fit_1'] + ' ' + self.main.dh.I_unit)
        q_fit_1_label.setFont(Const.css_plot_font)
        q_fit_1_label.setStyleSheet(Const.css_borders + ' ' + Const.css_plot_title)
        q_fit_1_label.setAlignment(Qt.AlignCenter)
        #Log.p_ms('fit_1...', self.first_time_ms)
        w.plots['fit_1'] = PlotMap(w, self.main, 'fit_1', q_fit_1_label)
        #Log.p_ms('fit_1 done.', self.first_time_ms)
            
        q_fit_2_label = QLabel(self.fit_labels['fit_2'] + ' km/s')
        q_fit_2_label.setFont(Const.css_plot_font)
        q_fit_2_label.setStyleSheet(Const.css_borders + ' ' + Const.css_plot_title)
        q_fit_2_label.setAlignment(Qt.AlignCenter)
        #Log.p_ms('fit_2...', self.first_time_ms)
        w.plots['fit_2'] = PlotMap(w, self.main, 'fit_2', q_fit_2_label)
        #Log.p_ms('fit_2 done.', self.first_time_ms)

        q_fit_3_label = QLabel(self.fit_labels['fit_3'] + ' km/s')
        q_fit_3_label.setFont(Const.css_plot_font)
        q_fit_3_label.setStyleSheet(Const.css_borders + ' ' + Const.css_plot_title)
        q_fit_3_label.setAlignment(Qt.AlignCenter)
        #Log.p_ms('fit_3...', self.first_time_ms)
        w.plots['fit_3'] = PlotMap(w, self.main, 'fit_3', q_fit_3_label)
        #Log.p_ms('fit_3 done.', self.first_time_ms)
                
        # ----- One window global layout / positions
        l_grid.setHorizontalSpacing(Const.layout_spacing)
        l_grid.setVerticalSpacing(Const.layout_spacing)
        l_grid.addWidget(f_win_header, 0, 0, 1, 3)
        
        l_grid.addWidget(q_x_y_label, 1, 0, 1, 1)
        l_grid.addWidget(q_lambda_y_label, 1, 1, 1, 1)
        l_grid.addWidget(q_lambda_I_label, 1, 2, 1, 1)
        
        l_grid.addWidget(f_x_y_options, 2, 0, 1, 1)
        l_grid.addWidget(f_lambda_y_options, 2, 1, 1, 1)
        l_grid.addWidget(q_fit_label, 2, 2, 1, 1)
        
        l_grid.addWidget(w.plots['x_y'].wp, 3, 0, 1, 1)
        l_grid.addWidget(w.plots['lambda_y'].wp, 3, 1, 1, 1)
        l_grid.addWidget(w.plots['lambda_I'].wp, 3, 2, 1, 1)
        
        l_grid.addWidget(f_bottom_plot1, 4, 0, 1, 1)
        l_grid.addWidget(f_bottom_plot2, 4, 1, 1, 1)
        l_grid.addWidget(q_lambda_I_title, 4, 2, 1, 1)
        
        l_grid.addWidget(q_fit_1_label, 5, 0, 1, 1)
        l_grid.addWidget(q_fit_2_label, 5, 1, 1, 1)
        l_grid.addWidget(q_fit_3_label, 5, 2, 1, 1)

        not_generated_text = 'Fit map is not generated yet.'
        self.main.qs_fit_label[win_key] = {}
        for i in range(3):
            plot_key = 'fit_' + str(i + 1)
            self.main.qs_fit_label[win_key][plot_key] = QLabel(not_generated_text)
            self.main.qs_fit_label[win_key][plot_key].setAlignment(Qt.AlignCenter)
            self.main.qs_fit_label[win_key][plot_key].setStyleSheet(Const.css_borders + ' ' + Const.css_plot_title)
            self.main.qs_fit_label[win_key][plot_key].setVisible(False)
            l_grid.addWidget(self.main.qs_fit_label[win_key][plot_key], 6, i, 1, 1)
            l_grid.addWidget(w.plots[plot_key].wp, 7, i, 1, 1)
                
        self.main.global_plots[win_key] = {'x_y': w.plots['x_y'], 'lambda_y': w.plots['lambda_y'],
            'lambda_I': w.plots['lambda_I'], 'fit_1': w.plots['fit_1'], 'fit_2': w.plots['fit_2'],
            'fit_3': w.plots['fit_3']}
        
        self.main.windows.append(w)
        self.l_flow.addWidget(w.f_win)
            
    @staticmethod
    def generateWindows(rt):
        if rt.main.dh is None:  # no fits loaded yet
            return
        try:
            rt.main.f_winc.q_win_text.deleteLater()
        except RuntimeError:  # already deleted
            pass

        """nb_windows_previous = 0  # previous data file
        if rt.main.are_data_loaded:  # data file(s) were already loaded
            nb_windows_previous = len(rt.main.windows)"""

        win_keys = rt.main.dh.data_info['win_keys']
        for i, win_key in enumerate(win_keys):
            """if i > nb_windows_previous - 1:  # win bloc not created yet
                Log.p('creating window bloc...')
                rt.main.f_winc.generateOneWindow(win_key, rt)
            else:
                Log.p('updating window bloc...')
                pass  # TODO else updateOneWindow"""
            rt.main.f_winc.generateOneWindow(win_key, rt)
        RunThread('OutOfSync', rt.main, -1, None, WindowsContainer.onceWindowsAreReady)

    @staticmethod
    def onceWindowsAreReady(rt):
        rt.main.are_data_loaded = True
        for win_key, plot_bloc in rt.main.global_plots.items():
            rt.main.update_vertical_bar(plot_bloc)
            plot_bloc['x_y'].fit_maps_bar_min.setValue(rt.main.dh.y_fit_bounds[win_key][0])
            plot_bloc['x_y'].fit_maps_bar_max.setValue(rt.main.dh.y_fit_bounds[win_key][1])
            viewRange = plot_bloc['x_y'].main_view_box.state['viewRange']
            plot_bloc['x_y'].initial_view_range = viewRange
            plot_bloc['fit_1'].initial_view_range = viewRange
            plot_bloc['fit_2'].initial_view_range = viewRange
            plot_bloc['fit_3'].initial_view_range = viewRange
            plot_bloc['x_y'].main_view_box.setLimits(xMin=viewRange[0][0],
                                                     xMax=viewRange[0][1] * Const.max_x_rescaling / Const.default_x_rescaling,
                                                     yMin=viewRange[1][0],
                                                     yMax=viewRange[1][1])
            for i in range(1, 4):
                plot_bloc['fit_' + str(i)].main_view_box.setLimits(xMin=viewRange[0][0],
                                                         xMax=viewRange[0][1] * Const.max_x_rescaling / Const.default_x_rescaling,
                                                         yMin=viewRange[1][0],
                                                         yMax=viewRange[1][1])

            viewRange = plot_bloc['lambda_y'].main_view_box.state['viewRange']
            plot_bloc['lambda_y'].initial_view_range = viewRange
            plot_bloc['lambda_y'].main_view_box.setLimits(xMin=viewRange[0][0],
                                                          xMax=viewRange[0][1] * Const.max_lambda_rescaling / Const.default_lambda_rescaling,
                                                          yMin=viewRange[1][0],
                                                          yMax=viewRange[1][1])
            # lambda_I limits updated in update_profile.py
        rt.main.link_axes()
        rt.main.f_menu.a_link_zoom()
        rt.main.f_menu.a_show_hide()
        rt.main.dh.init_fit_curves()
        rt.main.f_menu.update_generate_list()
        rt.main.is_loading_data = False

        for win_key, plot_bloc in rt.main.global_plots.items():
            plot_bloc['x_y'].viewAll()
            plot_bloc['lambda_y'].viewAll()

        if rt.main.python_state is not None:  # user is restoring a JSON state
            left_menu = rt.main.python_state['left_menu']
            widgets_to_restore = {
                'color_map': rt.main.f_menu.c_gradient_theme,
                'background': rt.main.f_menu.c_plot_bg,
                'show_hide': rt.main.f_menu.ks_show_hide,
                'fit_maps_list': rt.main.f_menu.c_generate_fit_maps,
                'is_global_level': rt.main.f_menu.r_global_levels,
                'level_min': rt.main.f_menu.i_level_min,
                'level_max': rt.main.f_menu.i_level_max,
                'level_method': rt.main.f_menu.c_level_method,
                'link_zoom': rt.main.f_menu.k_link_zoom,
                'x_rescaling': rt.main.f_menu.s_x_rescaling,
                'lambda_rescaling': rt.main.f_menu.s_lambda_rescaling,
                'plot_sizes': rt.main.s_plot_size
            }
            for key, widget in widgets_to_restore.items():
                c = type(widget).__name__
                if c == 'QComboBox':
                    widget.setCurrentIndex(left_menu[key])
                elif c == 'QSlider':
                    widget.setValue(left_menu[key])
                elif c == 'QCheckBox':
                    widget.setChecked(left_menu[key])
                elif c == 'QLineEdit':
                    widget.setText(str(left_menu[key]))
                elif c == 'dict':  # show/hide
                    for plot_key, k_show_hide in widget.items():
                        k_show_hide.setChecked(left_menu[key][plot_key])

            for win_key, py_window in rt.main.python_state['windows'].items():
                if py_window['x_y_average1D'] > 0:  # not default
                    rt.main.global_plots[win_key]['x_y'].c_average1D.setCurrentIndex(py_window['x_y_average1D'])
                elif py_window['x_y_average2D'] > 0:  # not default
                    rt.main.global_plots[win_key]['x_y'].c_average2D.setCurrentIndex(py_window['x_y_average2D'])
                if py_window['lambda_y_average1D'] > 0:  # not default
                    rt.main.global_plots[win_key]['lambda_y'].c_average1D.setCurrentIndex(py_window['lambda_y_average1D'])
                elif py_window['lambda_y_average2D'] > 0:  # not default
                    rt.main.global_plots[win_key]['lambda_y'].c_average2D.setCurrentIndex(py_window['lambda_y_average2D'])
            rt.main.python_state = None

        QApplication.restoreOverrideCursor()
        rt.main.f_menu.enable()
