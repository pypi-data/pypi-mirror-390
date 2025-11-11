#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import math
import os

from ..settings.const import Const
from ..utils.internal_utils import *
import numpy as np
import pyqtgraph as pg
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
from ..processing.threads.run_thread import RunThread
from ..logs.log import Log
import pyqtgraph.exporters

class PlotMap(): # 2 axes but plot is filled of values
    main = None
    w = None  # Window object
    wp = None  # GraphicsLayoutWidget
    iv = None  # ImageView
    init_levels = (0., 0.)  # intial levels of the ImageItem
    plot_key = ''  # plot key is 'x_y' or 'lambda_y',  ...
    q_label = None
    q_third_D_label = None
    vertical_bar = None  # InfiniteLine
    horizontal_bar = None
    fit_maps_bar_min = None  # to ignore dumbbells in fit maps
    fit_maps_bar_max = None
    fit_maps_y_min = Const.fit_maps_y_min
    fit_maps_y_max = Const.fit_maps_y_max
    f_options = None  # where average1D is
    f_bottom_plot = None
    bin_choice = 0
    average2D_choice = 0
    averaging = ''  # either '1D' or '2D', doing one cancels the other
    c_average1D = None
    c_average2D = None
    mouse_x = 0
    mouse_y = 0
    oc = None  # original cube
    # ac (averaged cube without leveling) is in PlotLine
    dc = None  # displayed cube (ave + level)
    np_without_level_data = None  # data with average but without leveling for I(lambda) display
    state_view_range = None
    initial_view_range = None
    is_map_refreshing = False

    def __init__(self, w, main, plot_key, q_label, q_third_D_label=None, f_bottom_plot=None,
                 f_options=None, c_average1D=None, c_average2D=None, gw_rt=None):
        # gw_rt: generateWindows_rt handles progress bar on data file load
        self.w = w
        self.w.wave_min, self.w.wave_max = main.dh.get_wavelength_range(self.w.win_key)
        self.wp = pg.GraphicsLayoutWidget()
        self.iv = pg.ImageView(parent=self.wp, view=pg.PlotItem())  # remove view=pg.PlotItem() to hide axes
        self.scene = self.main_plot_item.scene()  # GraphicsScene
        self.scene.sigMouseMoved.connect(self.a_mouse_moved)
        self.main = main
        self.plot_key = plot_key
        self.q_label = q_label
        self.q_third_D_label = q_third_D_label
        self.f_options = f_options
        self.f_bottom_plot = f_bottom_plot
        self.c_average1D = c_average1D
        self.c_average2D = c_average2D
        self.main_view_box.sigRangeChanged.connect(self.a_range_changed)

        self.setSize()
        self.hideMapElements()
        self.main_plot_item.invertY(False)

        if 'fit' not in plot_key:
            self.scene.sigMouseClicked.connect(self.a_mouse_double_clicked)

        RunThread('LoadPlotMap', self.main, self, None, PlotMap.setup_plot_map,
                  {'plot_map': self})
        if gw_rt is not None:
            gw_rt.progress_func(gw_rt.get_pf_dict(100. * 1 / (2 * self.main.dh.nb_windows)))

    def a_range_changed(self, main_view_box):
        self.state_view_range = main_view_box.state['viewRange']

    @staticmethod
    def link_maps(map1, map2, y_only=False):
        if not y_only:
            map1.main_plot_item.setXLink(map2.main_plot_item)
        map1.main_plot_item.setYLink(map2.main_plot_item)

    @staticmethod
    def setup_plot_map(rt):  # after LoadPlotMap in main thread to avoid display blackouts
        plot_map = rt.end_func_args['plot_map']
        plot_key = plot_map.plot_key

        plot_map.iv.show()

        # options ideas:
        #plot_map.scaleImage(0.5) axes values will be wrong then
        #print(plot_map.main_plot_item.vb.setBackgroundColor('y'))
        #plot_map.main_view_box.setBackgroundColor('y')
        #plot_map.ii.setOpts(opacity=0.3)
        #plot_map.ii.setCompositionMode(QPainter.CompositionMode(1))
        #plot_map.iv.frameTicks.setPen(pg.mkPen(cosmetic=False, width=45, color='r'))
        #print(plot_map.iv.ui, plot_map.iv.ui.histogram)
        #plot_map.iv.frameTicks.pen.setWidth(4)
        #plot_map.main_view_box.setBackgroundColor('y') # plot background
        #plot_map.iv.getRoiPlot().setBackground('y') # 3rd part plot background
        #plot_map.main_plot_item.setLabel('bottom', 'abscisse des data 2D')
        #plot_map.third_D_plot_item.setLabel('bottom', 'abscisse de la 3rd D des data')
        #plot_map.main_plot_item.getViewWidget().setBackground('y') # whole plot 2D background with axes
        #plot_map.iv.timeLine # infinite line, the 3rd D slider cursor

        if plot_map.dc is not None:
            if plot_key == 'x_y' or plot_key == 'lambda_y':
                plot_map.apply_image_data()
                plot_map.iv.timeLine.sigPositionChanged.connect(plot_map.update_third_D)
                plot_map.iv.timeLine.setPen(pg.mkPen(color=Const.slider_cursor_color,
                                                 width=Const.slider_cursor_width))
                plot_map.iv.timeLine.setHoverPen(pg.mkPen(color=Const.slider_cursor_color_h,
                                                      width=Const.slider_cursor_width))

                default_third_D_value = int(plot_map.dc.shape[0] / 2)  # middle position
                plot_map.init_third_D(default_third_D_value)

                plot_map.iv.getRoiPlot().setMinimumHeight(Const.slider_cursor_height)
                plot_map.third_D_plot_item.hideButtons()  # Hides the 'A' auto button
                plot_map.main_plot_item.hideButtons()  # Hides the 'A' auto button in main map
                if plot_key == 'x_y':
                    plot_map.init_fit_maps_bars()
            plot_map.viewAll()

        plot_bg = Const.bg_colors[Const.default_bg_color]
        plot_map.setPlotBackground(plot_bg)
        plot_map.init_levels = plot_map.ii.getLevels()
        plot_map.iv.setPredefinedGradient(Const.gradient_default_theme)

        """region = level_histogram.item.region
        region.setBrush(color=(255, 0, 0, 50)) change selected hist background"""
        plot_map.hide_level_ticks()

    @property
    def level_histogram(self):
        return self.iv.getHistogramWidget()

    @property
    def ii(self):
        return self.iv.getImageItem()

    @property
    def main_view_box(self):
        return self.ii.getViewBox()

    @property
    def main_plot_item(self):
        return self.iv.getView()

    @property
    def third_D_plot_item(self):
        return self.iv.getRoiPlot().getPlotItem()

    @property
    def third_D_value(self):
        return int(math.floor(self.iv.timeLine.value()))

    @property
    def x_or_t_value(self):
        return int(round(self.vertical_bar.value()))

    @property
    def y_value(self):
        return int(round(self.horizontal_bar.value()))

    @property
    def bin_number(self):
        if self.bin_choice > 0:
            third_dim = 'lambda'
            if self.plot_key == 'lambda_y':
                third_dim = self.main.dh.x_or_t
            average1D_values = self.main.dh.average1D_values(self, third_dim, True)
            return average1D_values[self.bin_choice]
        return 0

    @property
    def average2D_kernel_size(self):
        if self.average2D_choice > 0:
            return Const.average2D_kernel_sizes[self.average2D_choice]
        return 0

    def updateLimits(self, factor_x=1, factor_y=1):  # from initial view range
        viewRange = self.initial_view_range
        original_x_scale = Const.default_x_rescaling
        if self.plot_key == 'lambda_y':
            original_x_scale = Const.default_lambda_rescaling
        if viewRange is not None:
            self.main_view_box.setLimits(xMin=viewRange[0][0],
                                         xMax=round(viewRange[0][1] * factor_x / original_x_scale),
                                         yMin=viewRange[1][0],
                                         yMax=viewRange[1][1] * factor_y)

    def apply_transform(self):
        lambda_x_scale = 1
        lambda_x_translate = 0
        """if self.plot_key == 'lambda_y':
            lambda_x_scale = round((self.w.wave_max - self.w.wave_min) / self.main.dh.get_dim(self.w.win_key, 'lambda'), 1)
            lambda_x_translate = round(self.w.wave_min / lambda_x_scale, 1)"""

        abscissa_factor = self.main.abscissa_factor(self.plot_key)
        self.main_plot_item.getAxis('bottom').setScale(lambda_x_scale / abscissa_factor)

        tr = QTransform()
        tr.scale(abscissa_factor, 1)
        # if self.plot_key == 'x_y' or self.plot_key == 'lambda_y' or 'fit' in self.plot_key:
        y_translate = 0
        if 'fit' in self.plot_key:
            plot_bloc = self.main.get_plot_bloc(self)
            y_translate = min(plot_bloc['x_y'].fit_maps_y_min, plot_bloc['x_y'].fit_maps_y_max)
        tr.translate(lambda_x_translate - 0.5, y_translate - 0.5)  # even with step > 1, because of previous scale, offsetting x - 0.5 is fine
        self.ii.setTransform(tr)

    def apply_image_data(self):  # update self.dc before calling this
        state = self.main_plot_item.getViewBox().getState(True)

        """if self.plot_key == 'lambda_y':
            self.iv.setImage(self.dc, xvals=np.linspace(0.,)
        else:"""
        self.iv.setImage(self.dc, xvals=np.linspace(0., self.dc.shape[0] - 1, self.dc.shape[0]))
        self.apply_transform()
        self.main_plot_item.getViewBox().state['targetRange'] = state['viewRange']
        self.main_plot_item.getViewBox().updateViewRange()

    def hide_level_ticks(self):
        for tick in self.level_histogram.gradient.ticks:
            tick.hide()

    def a_mouse_moved(self, point):
        p = self.main_plot_item.vb.mapSceneToView(point)
        self.mouse_x = int(round(float(p.x()) / self.main.abscissa_factor(self.plot_key)))
        self.mouse_y = int(round(float(p.y())))

        # Handle arrow cursors on bars
        bars_to_apply = {
            'x_y': {
                    'h': [self.horizontal_bar, self.fit_maps_bar_min, self.fit_maps_bar_max],
                    'v': [self.vertical_bar]
            },
            'lambda_y': {'h': [self.horizontal_bar], 'v': [self.vertical_bar]}
        }
        QApplication.restoreOverrideCursor()
        for plot_key, bta in bars_to_apply.items():
            if plot_key == self.plot_key:
                for bar in bta['h']:
                    if bar is not None and bar.mouseHovering:
                        QApplication.setOverrideCursor(Qt.SizeVerCursor)
                for bar in bta['v']:
                    if bar is not None and bar.mouseHovering:
                        QApplication.setOverrideCursor(Qt.SizeHorCursor)

        font_tag = '<font color="' + Const.slider_cursor_color + '">'
        title_part = ' = ' + font_tag + str(self.mouse_x) + '</font>' + \
            ', y = ' + font_tag + str(self.mouse_y) + '</font>)'
        if self.plot_key == 'x_y' or 'fit' in self.plot_key:
            main_measure = 'I'
            if 'fit' in self.plot_key:
                main_measure = self.main.f_winc.fit_labels[self.plot_key].replace('(' + self.main.dh.x_or_t + ', y)', '')
            title = main_measure + '(' + self.main.dh.x_or_t + title_part
        elif self.plot_key == 'lambda_y':
            title = 'I(' + Const.lambda_char + title_part
        else:
            return
        if self.mouse_x >= 0 and self.mouse_y >= 0:
            mouse_y = self.mouse_y
            unit = ''
            factor = 1
            digits = Const.hover_digits
            try:
                if 'fit' in self.plot_key:
                    plot_bloc = self.main.get_plot_bloc(self)
                    mouse_y = int(self.mouse_y - plot_bloc['x_y'].fit_maps_bar_min.value())
                    mouse_cube = self.main.dh.fit_params_values[self.w.win_key][self.plot_key]
                    if self.plot_key == 'fit_2':
                        unit = ' km/s'  # converted in km/s in generate_fit_maps.run
                        digits = Const.hover_digits_v
                else:
                    fixed_third_D = self.third_D_value - 1  # TODO find a way to offset third D in pyqtgraph slider instead
                    if fixed_third_D < 0:
                        fixed_third_D = 0  # TODO block slider instead
                    mouse_cube = self.oc[fixed_third_D]

                title += ' = ' + font_tag + str(round(factor * mouse_cube[self.mouse_x][mouse_y], digits))
                title += '</font>' + unit
            except (IndexError, TypeError, KeyError):  # mouse is outside the data or data are not generated yet
                    pass
        self.q_label.setText(title)

    def a_mouse_double_clicked(self):
        if self.main.double_click:  # already clicked => it's a double click
            self.vertical_bar.setValue(round(self.mouse_x * self.main.abscissa_factor(self.plot_key)))
            self.horizontal_bar.setValue(round(self.mouse_y))
            self.main.f_winc.a_horizontal_bar_moved(self.horizontal_bar, self, True)
        else:  # first click
            # TODO FIX index carte + coherence img !! code 564721
            #####
            fixed_third_D = self.third_D_value - 1  # TODO find a way to offset third D in pyqtgraph slider instead
            if fixed_third_D < 0:
                fixed_third_D = 0  # TODO block slider instead
            #Log.p([self.mouse_x, self.mouse_y, fixed_third_D, str(self.oc[fixed_third_D][self.mouse_x][self.mouse_y])])
            ########
            self.main.double_click = True
            RunThread('MakeProcessAvailable', self.main, {'process': 'double_click',
                                                          'rate': Const.double_click_duration})

    def export(self):
        i_in_name = 1
        exporter = pg.exporters.ImageExporter(self.main_plot_item)
        output_file_name = 'output.png'
        while os.path.exists(output_file_name):
            output_file_name = 'output-' + str(i_in_name) + '.png'
            i_in_name += 1
        exporter.export(output_file_name)
        show_message('Plot exported', 'The plot has been exported as "' + output_file_name +
                     '" in the project folder.<br><br><b>To export with more options, use the right click' + \
                     ' -> "Export..." option.')
    
    def refresh(self):  # refreshes map
        self.is_map_refreshing = True
        if self.dc is None:
            if self.plot_key == 'x_y' or self.plot_key == 'lambda_y':
                self.main.dh.update_map_data(self)
        previous_third_D_value = self.third_D_value

        if self.dc is not None:  # case of other "not generated" fit_1 maps
            if self.plot_key == 'fit_1':
                self.dc = self.main.dh.get_leveled_cube(self.dc)
                self.apply_image_data()
            elif 'fit' not in self.plot_key:
                self.apply_image_data()
                self.set_third_D_value(previous_third_D_value)  # Restore third D value
                self.iv.autoLevels()
        self.is_map_refreshing = False
    
    def set_third_D_value(self, third_D_value, label_only=False):
        if self.plot_key == 'x_y' or 'fit' in self.plot_key:
            label = 'Wavelength ' + Const.lambda_char + ' index'
        elif self.plot_key == 'lambda_y':
            dim_name = 'Date' if self.main.dh.is_sas else 'Position'
            label = dim_name + ' ' + self.main.dh.x_or_t + ' index'
        else:
            Log.p('update_third_D got a wrong plot_key, ' + self.main.dh.x_or_t + '_y or' +
                  ' lambda_y are authorized.', 'error')
            return

        if self.plot_key == 'x_y' or 'fit' in self.plot_key:
            label += ' = ' + str(third_D_value) + ' (' + \
                     str(round(self.main.dh.lambda_index_to_unit(self.w, third_D_value), 1)) + ' Å)'
        else:
            label += ' = ' + str(third_D_value)

        self.q_third_D_label.setText(label)
        if not label_only:
            self.iv.timeLine.setValue(int(third_D_value))
            # it will call update_third_D() because of the connected method
            
    def a_average1D(self, bin_choice):  # average on neighbors
        self.bin_choice = bin_choice
        if self.plot_key == 'x_y':  # average over lambda
            curr_bin = self.bin_number
            if curr_bin == 0:
                curr_bin = 1  # means no average
            self.main.nb_available_bin[self.w.win_key] = int(self.main.dh.get_dim(self.w.win_key, 'lambda') / curr_bin)
        self.averaging = '1D'
        third_D_name = Const.lambda_char
        map_name = 'I(x, y)'
        if self.plot_key == 'lambda_y':
            third_D_name = 'x'
            map_name = 'I(' + Const.lambda_char + ', y)'
        thread_name = 'Averaging 1D ' + map_name + ' over ' + third_D_name + ' (' + str(self.bin_number) + \
                      ' ' + third_D_name + ')'
        if self.bin_choice == 0:
            thread_name = 'Resetting average 1D over ' + third_D_name
        RunThread('ComputeAverage', self.main, self, thread_name)

    def a_average_whole_dim(self, c_average, value):
        c_average.setCurrentIndex(value)  # will trigger self.a_average1D

    def a_average2D(self, average2D_choice):
        self.average2D_choice = average2D_choice
        self.averaging = '2D'
        map_name = 'I(x, y)'
        if self.plot_key == 'lambda_y':
            map_name = 'I(' + Const.lambda_char + ', y)'
        thread_name = 'Averaging 2D ' + map_name + ' kernel ' + str(self.average2D_kernel_size) + 'x' + \
                      str(self.average2D_kernel_size)
        if self.average2D_choice == 0:
            thread_name = 'Resetting average 2D ' + map_name
        RunThread('ComputeAverage', self.main, self, thread_name)
    
    def setPlotBackground(self, plot_bg):
        self.main_plot_item.getViewWidget().setBackground(plot_bg)
        self.iv.getRoiPlot().setBackground(plot_bg)
        if self.horizontal_bar is not None and self.vertical_bar is not None:  # already done the first time
            self.horizontal_bar.setPen(get_cross_pen(map_background=plot_bg))
            self.horizontal_bar.setHoverPen(get_cross_pen(True, plot_bg))
            self.vertical_bar.setPen(get_cross_pen(map_background=plot_bg))
            self.vertical_bar.setHoverPen(get_cross_pen(True, plot_bg))

    def setup_horizontal_bars(self):
        len_y = self.main.dh.get_dim(self.w.win_key, 'y')
        self.horizontal_bar = self.main_plot_item.addLine(movable=True, bounds=[0, len_y - 1], x=None,
                                                          y=Const.default_y_index,
                                                          pen=get_cross_pen(),
                                                          hoverPen=get_cross_pen(True))
        self.horizontal_bar.sigPositionChanged.connect(lambda: self.main.f_winc.a_horizontal_bar_moved(
            self.horizontal_bar, self))
        self.horizontal_bar.sigPositionChangeFinished.connect(lambda: self.main.f_winc.a_horizontal_bar_moved(
            self.horizontal_bar, self, True))

    def setup_vertical_bars(self):
        len_third_D = self.main.dh.get_adjusted_third_D(self)
        self.vertical_bar = self.main_plot_item.addLine(movable=True, bounds=[0, len_third_D - 2], x=0, y=None,
                                                        pen=get_cross_pen(),
                                                        hoverPen=get_cross_pen(True))
        self.vertical_bar.sigPositionChanged.connect(lambda: self.main.f_winc.a_vertical_bar_moved(
            self.vertical_bar, self))
        self.vertical_bar.sigPositionChangeFinished.connect(lambda: self.main.f_winc.a_vertical_bar_moved(
            self.vertical_bar, self, True))

    def init_third_D(self, default_third_D_value):
        self.set_third_D_value(default_third_D_value)
        self.setup_vertical_bars()
        self.setup_horizontal_bars()

    def init_fit_maps_bars(self):
        self.fit_maps_bar_min = self.main_plot_item.addLine(movable=True,
                                                    bounds=[Const.fit_maps_y_min, Const.fit_maps_y_max],
                                                    x=None, y=Const.fit_maps_y_min_default,
                                                    pen=pg.mkPen(Const.fit_maps_bar_color,
                                                                 width=Const.fit_maps_bar_width),
                                                    hoverPen=pg.mkPen(Const.fit_maps_bar_color,
                                                                      width=Const.fit_maps_bar_width_hover)
                                                    )
        self.fit_maps_bar_min.sigPositionChangeFinished.connect(
            lambda: self.main.f_winc.fit_maps_bar_moved(self))

        self.fit_maps_bar_max = self.main_plot_item.addLine(movable=True,
                                                    bounds=[Const.fit_maps_y_min, Const.fit_maps_y_max],
                                                    x=None, y=Const.fit_maps_y_max_default,
                                                    pen=pg.mkPen(Const.fit_maps_bar_color,
                                                                 width=Const.fit_maps_bar_width),
                                                    hoverPen=pg.mkPen(Const.fit_maps_bar_color,
                                                                      width=Const.fit_maps_bar_width_hover)
                                                    )
        self.fit_maps_bar_max.sigPositionChangeFinished.connect(
            lambda: self.main.f_winc.fit_maps_bar_moved(self))


    def update_third_D(self):
        if self.is_map_refreshing:
            return
        if self.plot_key == 'lambda_y':  # The user just changed the third D "x"
            for win_key, plot_bloc in self.main.global_plots.items():
                plot_bloc['lambda_y'].set_third_D_value(self.third_D_value)
                if self.main.are_data_loaded:
                    plot_bloc['lambda_I'].updatePlotData()
        else:
            self.set_third_D_value(self.third_D_value, True)
            
        plot_bloc = self.main.get_plot_bloc(self)
        if plot_bloc is not None:  # if None then it's the first load,
            # All plots are not available yet, WindowsContainer handles the first one
            # Vertical bar updates once plots are available
            self.main.update_vertical_bar(plot_bloc)
            
    def scaleImage(self, scale_x, scale_y):
        tr = QTransform()
        tr.scale(scale_x, scale_y)
        if self.plot_key == 'x_y' or self.plot_key == 'lambda_y' or 'fit' in self.plot_key:
            tr.translate(-0.5, -0.5)  # even with step > 1, because of previous scale, offsetting x - 0.5 is fine
        self.ii.setTransform(tr)
              
    def hideMapElements(self, keep_histogram=True):
        if not keep_histogram:
            self.iv.ui.histogram.hide()
        self.iv.ui.roiBtn.hide()
        self.iv.ui.menuBtn.hide()
        self.main_plot_item.ctrlMenu = None  # remove Plot options

    def viewAll(self):
        self.main_plot_item.autoRange()  # same as right click -> View All
        
    def show_hide(self, show_it):  # keeps height to hide width dynamically
        width = self.main.s_plot_size.value() if show_it else 0
        if 'fit' in self.plot_key:
            height = self.main.s_plot_size.value() if show_it else 0
            if show_it:
                is_generating = self.w.win_key in self.main.fit_maps_are_generating and self.main.fit_maps_are_generating[self.w.win_key]
                if not is_generating and not self.main.fit_maps_warning:
                    self.main.fit_maps_warning = True
                    if len(self.main.fit_maps_are_generated) == 0 and len(self.main.fit_maps_are_generating) == 0 and self.main.python_state is None:
                        show_message('Fit maps warning', 'In order to see the fit maps results, ' +
                            'please use the "Generate fit maps" option in the menu.')
                if self.w.win_key in self.main.fit_maps_are_generated and self.main.fit_maps_are_generated[self.w.win_key]:
                    self.main.qs_fit_label[self.w.win_key][self.plot_key].setVisible(False)
                    self.setSize(width, height)
                else:
                    self.main.qs_fit_label[self.w.win_key][self.plot_key].setVisible(True)
            else:
                self.main.qs_fit_label[self.w.win_key][self.plot_key].setVisible(False)
                self.setSize(width, height)
        else: # x_y and lambda_y
            self.q_third_D_label.setFixedWidth(width)
            self.f_options.setFixedWidth(width)
            height = self.main.s_plot_size.value()
            self.setSize(width, height)
        self.q_label.setFixedWidth(width)
        if show_it and self.plot_key == 'x_y':
            self.viewAll()
        
    def setSize(self, width=None, height=None):
        if width is None:
            width = self.main.s_plot_size.value()
        if height is None:
            height = self.main.s_plot_size.value()
            
        self.wp.setMinimumWidth(width)
        self.wp.setMaximumWidth(width)
        self.iv.setMinimumWidth(width)
        self.iv.setMaximumWidth(width)
        self.q_label.setFixedWidth(width)
        if self.q_third_D_label is not None:
            self.q_third_D_label.setFixedWidth(width)
        if self.f_options is not None:
            self.f_options.setFixedWidth(width)
        if 'fit' not in self.plot_key:
            self.f_bottom_plot.setFixedWidth(width)
        self.wp.setMinimumHeight(height)
        self.wp.setMaximumHeight(height)
        if height > 0:
            self.iv.setMinimumHeight(height)
            self.iv.setMaximumHeight(height)
