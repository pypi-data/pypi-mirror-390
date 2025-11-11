#!/usr/bin/env python3

import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication

from ..processing.fit import *
from ..utils.internal_utils import get_ms, get_cross_pen
from ..logs.log import Log
from ..processing.threads.run_thread import RunThread
from PyQt5.QtCore import Qt
from ..processing.threads.workers.update_profile import UpdateProfile


class PlotLine():  # 2 axes with a common curve line
    main = None
    w = None  # Window object
    wp = None  # GraphicsLayoutWidget
    main_plot_item = None
    plot_data_item = None
    fit_plot_data_item = None
    plot_key = ''
    q_label = None  # QLabel plot title
    q_footer_label = None  # below I(lambda)
    min_intensity = None
    max_intensity = None
    ac = None  # averaged cube (without leveling) x_y map's shape is used i.e. (lambda, x, y)
    vertical_bar = None
    scene = None  # GraphicsScene

    def __init__(self, w, main, plot_key, x_index, q_label, q_fit_label, q_footer_label):
        super().__init__()
        self.wp = pg.GraphicsLayoutWidget()
        self.main = main
        self.w = w
        self.plot_key = plot_key
        self.q_label = q_label
        self.q_fit_label = q_fit_label
        self.q_footer_label = q_footer_label

        self.main_plot_item = self.wp.addPlot()
        self.main_plot_item.ctrlMenu = None  # remove Plot options
        self.updatePlotData(x_index, Const.default_y_index)
        self.main_plot_item.showGrid(x=True, y=True)
        self.setSize()

        self.scene = self.main_plot_item.scene()  # GraphicsScene
        self.scene.sigMouseMoved.connect(self.a_mouse_moved)

        self.vertical_bar = self.main_plot_item.addLine(movable=True, bounds=[0, self.dim_lambda],
                                                        x=0, y=None,
                                                        pen=get_cross_pen(force_color="#888"),
                                                        hoverPen=get_cross_pen(True,
                                                                               force_color="#888"))
        self.vertical_bar.sigPositionChanged.connect(lambda: self.a_move_vertical_bar(self.vertical_bar))

        plot_bg = Const.bg_colors[Const.default_bg_color]
        self.setPlotBackground(plot_bg)

    @property
    def main_view_box(self):
        return self.main_plot_item.vb

    @property
    def dim_lambda(self):
        return self.main.dh.get_dim(self.w.win_key, 'lambda')

    def get_K_bounds(self):
        offset_b_min = round(np.nanpercentile(self.ac, Const.offset_bound_1), Const.fit_pc_digits)
        offset_b_max = round(np.nanpercentile(self.ac, Const.offset_bound_2), Const.fit_pc_digits)
        return offset_b_min, offset_b_max

    def a_mouse_moved(self):
        if self.vertical_bar is not None and self.vertical_bar.mouseHovering:
            QApplication.setOverrideCursor(Qt.SizeHorCursor)
        else:
            QApplication.restoreOverrideCursor()

    def a_move_vertical_bar(self, bar):
        plot_bloc = self.main.get_plot_bloc(self)
        self.main.lambda_I_bar_moves = True
        plot_bloc['lambda_y'].vertical_bar.setValue(int(bar.value() * self.main.abscissa_factor('lambda_y')))
        self.main.lambda_I_bar_moves = False

    @staticmethod
    def finish_updating(rt):
        if rt.end_func_args is None or 'profile_data' not in rt.end_func_args:
            Log.p('UpdateProfile did not finish well.', 'warn')
            return
        win_key = rt.end_func_args['win_key']
        profile_data = rt.end_func_args['profile_data']
        plot_line = profile_data['plot_line']
        hist_data = profile_data['hist_data']
        fit_data = profile_data['fit_data']
        fit_params = profile_data['fit_params']
        chi2 = profile_data['chi2']
        fit_exists = len(fit_params) > 0

        plot_line.updateLimits()

        if plot_line.plot_data_item is None:  # First load
            plot_line.plot_data_item = plot_line.main_plot_item.plot(hist_data[0], hist_data[1],
                                                            pen=pg.mkPen(Const.plot_line_color,
                                                                         width=Const.plot_line_width),
                                                                         stepMode='center')
            if fit_exists and not rt.main.dh.is_full_spectrum:
                plot_line.fit_plot_data_item = plot_line.main_plot_item.plot(fit_data[0], fit_data[1],
                                                                        pen=pg.mkPen(Const.fit_plot_line_color,
                                                                                     width=Const.fit_plot_line_width))
        else:
            plot_line.plot_data_item.setData(hist_data[0], hist_data[1])
            if fit_exists and not rt.main.dh.is_full_spectrum:
                plot_line.fit_plot_data_item.setData(fit_data[0], fit_data[1])

        #plot_line.main_plot_item.autoRange()  # same as right click -> View All
        lambdaMin, lambdaMax, Imin, Imax = plot_line.get_limits()
        plot_line.main_plot_item.setRange(xRange=[-lambdaMin, lambdaMax], yRange=[Imin, Imax])
        if not rt.main.dh.is_full_spectrum:
            fit_label = 'No fit found (at least ' + str(Const.min_bins_to_fit) + ' bins required)'
            if fit_exists:
                fit_label = fit_params_to_str(fit_params, chi2)
            else:
                plot_line.fit_plot_data_item.setData([0], [0])
            plot_line.q_fit_label.setText(fit_label)

        RunThread('MakeProcessAvailable', rt.main,
                  {'win_key': win_key, 'rate': Const.thread_rate, 'process': 'updating_profile'})

    def get_limits(self):  # returns lambdaMin, lambdaMax, Imin, Imax
        padding_I = Const.profile_padding_I_pc * self.max_intensity
        return -Const.profile_padding_lambda, \
            self.dim_lambda + Const.profile_padding_lambda, \
            self.min_intensity - padding_I, \
            self.max_intensity + padding_I

    def updateLimits(self):
        lambdaMin, lambdaMax, Imin, Imax = self.get_limits()
        self.main_view_box.setLimits(xMin=lambdaMin, xMax=lambdaMax, yMin=Imin, yMax=Imax)

    def refresh(self):  # name used for PlotLine and PlotMap
        self.updatePlotData()

    def updatePlotData(self, x_index=None, y_index=None):
        # x_index and y_index are provided integers on first load
        # keep them None for updating profile with current user x,y values
        objects = {'plot_line': self, 'x_index': x_index, 'y_index': y_index}
        plot_bloc = self.main.get_plot_bloc(self)  # /!\ None on first load
        if x_index is not None:
            RunThread('UpdateProfile', self.main, objects, None, PlotLine.finish_updating, {'win_key': self.w.win_key})
        # if init_third_D finished
        elif (plot_bloc['x_y'].horizontal_bar is not None and plot_bloc['lambda_y'].horizontal_bar is not None) and \
            (self.main.force_third_D or
                (
                    self.w.win_key not in self.main.updating_profile or
                    self.main.updating_profile[self.w.win_key] is False
                )
        ):
            self.main.updating_profile[self.w.win_key] = True
            RunThread('UpdateProfile', self.main, objects, None, PlotLine.finish_updating, {'win_key': self.w.win_key})

    def setPlotBackground(self, plot_bg):  # do not remove, called for PlotMap or PlotLine objects
        self.wp.setBackground(plot_bg)

    def show_hide(self, show_it): # keeps height to hide width dynamically
        width = self.main.s_plot_size.value() if show_it else 0
        height = self.main.s_plot_size.value()
        self.q_label.setFixedWidth(width)
        self.q_fit_label.setFixedWidth(width)
        self.q_footer_label.setFixedWidth(width)
        self.setSize(width, height)

    def setSize(self, width = None, height = None):
        if width is None:
            width = self.main.s_plot_size.value()
        if height is None:
            height = self.main.s_plot_size.value()
        self.q_label.setFixedWidth(width)
        self.q_fit_label.setFixedWidth(width)
        self.q_footer_label.setFixedWidth(width)
        self.wp.setMaximumWidth(width)
        self.wp.setMaximumHeight(height)
        self.wp.setMinimumWidth(width)
        self.wp.setMinimumHeight(height)
