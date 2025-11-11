#!/usr/bin/env python3
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import os

BASE_DIR = os.path.dirname(__file__) + '/..'

class Const:
    # Basic constants
    lambda_char = chr(955)
    mu_char = chr(956)
    sigma_char = chr(963)

    # Basics
    default_data_path = '/home/dpicard/Documents/fits/'  # where the folder level2/ is
    default_data_path_state = BASE_DIR + '/settings/states/'
    debug_mode = False
    log_file = 'debug.log'  # think to git ignore this if you change the name
    window_width = 1920
    window_height = 900
    title_margin = 10  # next to Menu, Windows titles
    date_format = "%Y-%m-%dT%H:%M:%S"
    layout_spacing = 2  # pixels between buttons, texts... in layouts
    css_borders = 'border: 1px solid white;'
    css_plot_title = 'padding: 2px;'
    css_plot_font = QFont('Arial', 12, weight=QFont.Bold)
    css_window_font = QFont('Arial', 17, weight=QFont.Bold)
    colored_text = '<font color="#00aaff"><b>'
    end_colored_text = '</b></font>'
    double_click_duration = 0.5  # sec

    thread_rate = 0.2  # sec
    restore_force_third_D = 0.5  # sec, after mouse click finished
    max_pending = 10  # secs, kill some threads or processes after this time
    # Too small could freeze sliders (especially 3rd D of I(lambda, y))
    # This should be fixed
    # ------ End Basics

    # Form fields
    label_disabled = 'color: #555;'
    label_enabled = 'color: white;'
    button_disabled = 'background-color: #333; color: #555;'
    button_enabled = 'color: white; background-color: #333;'
    footer_button = 'padding: 1px 3px;'
    # ------ End form fields

    # Menu
    level_input_width = 100
    recent_files_path = BASE_DIR + '/settings/recent_files.txt'
    tooltip_color = 'black'
    tooltip_background = 'white'
    # ------ End Menu

    # Plots
    default_plot_size = 450
    min_plot_size, min_plot_size_pc = 200, 20  # px, % equivalent displayed
    max_plot_size, max_plot_size_pc = 1000, 200  # px, % equivalent displayed
    default_font_size = 11
    min_font_size, min_font_size_pc = 4, 37  # px, % equivalent displayed
    max_font_size, max_font_size_pc = 22, 200  # px, % equivalent displayed
    level_sensibility = 0.02
    # new level system:
    level_methods = ['Linear', 'Logarithm', 'Square root']
    default_min = '1'
    default_max = '99'
    max_lambda_rescaling = 30  # scaling abscissa only in I(lambda, y)
    default_lambda_rescaling = 15
    max_x_rescaling = 10  # scaling x only in I(x, y) and fit maps
    default_x_rescaling = 1
    gradient_themes = ['thermal', 'flame', 'yellowy', 'bipolar', 'spectrum',
                       'cyclic', 'greyclip', 'grey', 'viridis', 'inferno', 'plasma', 'magma']
    gradient_default_theme = 'viridis'
    bg_colors = {'Black': '#000000', 'White': '#FFFFFF'}  # values must match pyqtgraph.mkColor
    # Careful: white and black are used to determinate the cross bar color, see cross_bar_* variables
    default_bg_color = 'Black'  # must be a key of the above dict
    plot_line_color = '#0aff6c'
    plot_line_width = 1
    default_y_index = 512
    average2D_choices = ['1x1 (no smoothing)', '3x3', '5x5', '7x7']  # /!\ Adapt average2D_kernel_sizes
    average2D_kernel_sizes = [0, 3, 5, 7]
    profile_padding_lambda = 1  # padding added
    profile_padding_I_pc = 0.05  # padding pourcentage above/below profile plot
    hover_digits = 5  # nb digits on mouse hover (I value)
    hover_digits_v = 1 # nb digifts for velocity maps

    # Third dimension (bottom of a plot around the 3rd dimension slider)
    slider_cursor_color = '#0084ff'  # also updates related texts
    slider_cursor_color_h = '#003cff'  # when mouse hovering
    slider_cursor_width = 5
    slider_cursor_height = 40
    """The default position is middle, see PlotMap.py:PlotMap() constructor to change it
    (look for default_third_D_value)"""
    cross_bar_color = {'#000000': 'white', '#FFFFFF': 'black'}  # key is map background, value is the associated bar color
    cross_bar_color_hover = {'black': '#00ff00', 'white': '#00ff00'}
    cross_bar_width = 2
    cross_bar_width_hover = 3
    # ------ End Third dimension (bottom of a plot)

    # Fit and fit maps
    min_bins_to_fit = 4
    fit_plot_line_color = '#9d00b9'
    fit_text_color = '#c75fe1'
    fit_plot_line_width = 2
    fit_nb_digits = 3
    fit_resolution = 20  # interpolation in profile
    chi2_digits = 2
    fit_maps_y_min = 0
    fit_maps_y_max = 1024
    fit_maps_y_min_default = 100  # changed to dh.y_fit_bounds according to data
    fit_maps_y_max_default = 900  # changed to dh.y_fit_bounds according to data
    fit_maps_bar_color = '#ff0000'
    fit_maps_bar_width = 2
    fit_maps_bar_width_hover = 3
    offset_bound_1 = 0  # % percentile, 50 means median
    offset_bound_2 = 100
    # offset_hint is average between offset bounds
    sigma_bound_1 = 3 / 2.355
    sigma_bound_2 = 24 / 2.355
    sigma_hint = 6 / 2.355
    fit_pc_min, fit_pc_max = 0.8, 1.2  # used for I_max hint and lambda_max hint
    fit_pc_digits = 3
    # ------ End Fit maps

    # ------ End Plots

    # ------ Footer
    progress_bar_height = 9
    progress_bar_color = '#006fd1'
    green_text = '#26b100'
    progress_bar_color_done = '#1a7800'
    red_text = '#ff5a5d'
    progress_bar_interrupt_color = '#b30003'
    # ------ End Footer

