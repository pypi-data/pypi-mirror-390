from functools import partial
import json
from ..utils.internal_utils import *
from PyQt5.QtWidgets import *
from pylab import *
from ..logs.log import Log
import os
from ..settings.const import Const

class MenuBar(QMenuBar):
    main = None
    menus = None
    m_list = []
    a_no_recent = None
    subm_recent_files = None

    def __init__(self, main):
        super(MenuBar, self).__init__()
        self.main = main
        self.menus = {
            'File': [  # [icon name, submenu text, triggered function] (exception for recent files)
                ['SP_DialogOpenButton', 'Open data file (.fits)', 'Ctrl+O', self.main.f_header.a_load_fits],
                #['SP_DialogCancelButton', 'Unload data', '', a_unload],
                ['SP_DirLinkIcon', 'Recent files history', '<not possible>', 'recent_files'],
                ['SP_BrowserStop', 'Clear recent files history', 'Ctrl+H', self.a_clear_recent_files],
            ],
            'Edit': [
                ['SP_BrowserReload', 'Refresh plots', 'Ctrl+R', self.a_refresh_plots]
            ],
            'State': [
              ['SP_DialogOpenButton', 'Load state', 'Ctrl+Shift+L', self.a_load_state],
              ['SP_DriveFDIcon', 'Save state', 'Ctrl+Shift+S', self.a_save_state],
              ['SP_DriveFDIcon', 'Save state online?', 'Ctrl+Shift+O', self.a_save_state]
            ],
            '?': [
                ['SP_MessageBoxQuestion', 'User documentation', '', self.a_user_documentation],
                ['SP_MessageBoxInformation', 'About / Contact us', '', self.a_about]
            ]
        }
        self.main.setMenuBar(self)

        for m_text, ma_blocs in self.menus.items():
            m = QMenu('&' + m_text, self.main)
            self.addMenu(m)
            tb = self.main.addToolBar(m_text)
            for ma_bloc in ma_blocs:  # ma (menu action) is a submenu (QAction)
                if ma_bloc[3] == 'recent_files':
                    self.subm_recent_files = m.addMenu(ma_bloc[1])
                    self.subm_recent_files.setIcon(get_icon(ma_bloc[0]))
                    self.set_recent_files()
                else:
                    ma_ = QAction('&' + ma_bloc[1], self.main)
                    if ma_bloc[0] != '':
                        ma_.setIcon(get_icon(ma_bloc[0]))
                    ma_.triggered.connect(ma_bloc[3])
                    if ma_bloc[2] != '':
                        ma_.setShortcut(ma_bloc[2])
                    m.addAction(ma_)
                    tb.addAction(ma_)

    def a_load_state(self):
        q_state_file = QFileDialog.getOpenFileName(self, 'Open file',
                                                   Const.default_data_path_state, '*.json')
        state_path = q_state_file[0]
        if state_path == '':  # cancel
            return
        with open(state_path, 'r') as file:
            python_state = json.load(file)
            self.main.python_state = python_state
            self.main.f_header.a_load_fits(python_state['fits_file_folder'] + python_state['fits_file_name'])

    def a_save_state(self):
        python_show_hide = {}
        for plot_key, k_show_hide in self.main.f_menu.ks_show_hide.items():
            python_show_hide[plot_key] = self.main.f_menu.ks_show_hide[plot_key].isChecked()
        python_windows = {}

        for win_key, plot_bloc in self.main.global_plots.items():
            w = plot_bloc['x_y'].w
            x_y = plot_bloc['x_y']
            lambda_y = plot_bloc['lambda_y']
            python_windows[win_key] = {
                'local_levels': {'min': float(w.levels['min'].text()),
                                 'max': float(w.levels['max'].text()),
                                 'method': w.levels['method'].currentIndex()},
                'x_y_average1D': x_y.c_average1D.currentIndex(),
                'x_y_average2D': x_y.c_average2D.currentIndex(),
                'lambda_y_average1D': lambda_y.c_average1D.currentIndex(),
                'lambda_y_average2D': lambda_y.c_average2D.currentIndex(),
                'x_or_t': plot_bloc['x_y'].x_or_t_value,  # white cross position
                'y': w.plots['x_y'].y_value,
                'lambda': w.plots['x_y'].third_D_value,
                'fit_maps_bar_min': w.plots['x_y'].fit_maps_bar_min.value(),
                'fit_maps_bar_max': w.plots['x_y'].fit_maps_bar_max.value()
                # add user's fit bounds
            }
        python_state = {
            'fits_file_name': self.main.f_header.data_file_basename,
            'fits_file_folder': self.main.f_header.data_path.replace(self.main.f_header.data_file_basename, ''),
            'left_menu': {
                'color_map': self.main.f_menu.c_gradient_theme.currentIndex(),
                'background': self.main.f_menu.c_plot_bg.currentIndex(),
                'show_hide': python_show_hide,
                'fit_maps_list': self.main.f_menu.c_generate_fit_maps.currentIndex(),
                'is_global_level': self.main.f_menu.r_global_levels.isChecked(),
                'level_min': float(self.main.f_menu.i_level_min.text()),
                'level_max': float(self.main.f_menu.i_level_max.text()),
                'level_method': self.main.f_menu.c_level_method.currentIndex(),
                'link_zoom': self.main.f_menu.k_link_zoom.isChecked(),
                'x_rescaling': self.main.f_menu.s_x_rescaling.value(),
                'lambda_rescaling': self.main.f_menu.s_lambda_rescaling.value(),
                'plot_sizes': self.main.s_plot_size.value()
            },
            'windows': python_windows
        }
        json_state = json.dumps(python_state)
        name = QFileDialog.getSaveFileName(self, 'Save File', '', 'Quicklook state (*.json)')
        name = name[0]
        if name != '':
            file = open(name, 'w')
            file.write(json_state)
            file.close()

    def a_clear_recent_files(self):
        os.remove(Const.recent_files_path)
        self.subm_recent_files.clear()
        self.set_no_recent_file_action()
        show_message('Recent files history cleared', 'Recent files history has been cleared.')

    def set_no_recent_file_action(self):
        self.a_no_recent = self.subm_recent_files.addAction('No recent file found, load a data file first')
        self.a_no_recent.setEnabled(False)

    def set_recent_files(self):
        no_recent_files = True
        content = ''

        if os.path.exists(Const.recent_files_path):
            file = open(Const.recent_files_path, "r")
            content = file.read()
            no_recent_files = '.fits' not in content
            file.close()
        else:
            file = open(Const.recent_files_path, "w")
            file.close()

        if no_recent_files:
            self.set_no_recent_file_action()
        else:
            recent_files = content.split('\n')
            recent_files_fits = []
            for recent_file in recent_files:
                if '.fits' in recent_file:
                    recent_files_fits.append(recent_file)
            a = self.subm_recent_files.addAction('Loaded dates times - Path of data FITS files')
            self.subm_recent_files.setStyleSheet('color: white;')
            a.setEnabled(False)
            for i, recent_file in enumerate(recent_files_fits):
                li = recent_file.rsplit(' ', 1)
                recent_file = ' - '.join(li)
                a = self.subm_recent_files.addAction(recent_file)
                if i == len(recent_files_fits) - 1:
                    a.setShortcut('Ctrl+L')
                a.triggered.connect(partial(self.main.f_header.a_load_fits, recent_file.split(' ')[-1]))

    def a_refresh_plots(self):
        self.main.f_menu.a_reset_zoom()  # temp
        # TO DO move this in thread
        """self.main.f_menu.a_show_hide()
        if self.main.are_data_loaded:
            for plot in self.main.all_plots():
                if plot.plot_key == 'x_y' or plot.plot_key == 'lambda_y': # refresh maps data
                    plot.refresh()"""


    def a_user_documentation(self):
        show_message('User documentation',
                     'Go to <a href="https://git.ias.u-psud.fr/spice/data_quicklook" style="color: lightblue;">IAS Gitlab Quicklook project</a>')

    def a_about(self):
        show_message('About us', 'This application has been developed at IAS.<br>' +
                     'spice-ops.ias@universite-paris-saclay.fr')

