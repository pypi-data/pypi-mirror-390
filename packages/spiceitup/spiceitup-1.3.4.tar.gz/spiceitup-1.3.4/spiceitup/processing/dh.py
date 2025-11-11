#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sunraster.instr.spice import _read_single_spice_l2_fits
import numpy as np
import math
import time
from ..logs.log import Log
from ..toolbox.binning import rebinGabriel
from ..utils.internal_utils import *
import cv2
from ..settings.const import Const

class DataHandling():
    main = None
    data_info = None
    raster = None  # will be free after set_data_info
    cube = None
    is_sas = False  # STUDYTYP == "Sit-and-stare"
    is_full_spectrum = False  # STUDYTYP == "Single Exposure"
    # otherwise data file is raster
    x_or_t = ''  # 't' if is_sas else 'x'
    fit_params_values = {}
    cube_ready_fit = {}
    dims = {}  # key: win_key, key2: dimension, value = dimension length
    original_cubes = {}  # original cubes dict: {window_key: numpy_cube, ... }
    win_info = {}  # {win_key: {{win_info}}, ...}
    first_meta = None
    wave = {}  # {win_key: {'min': WAVEMIN, 'max': WAVEMAX, 'unit': WAVEUNIT}, ... } # nm
    y_fit_bounds = {} # {win_key: [min, max]} used for fit bars limits
    I_unit = ''

    def __init__(self):
        self.main = None
        self.data_info = None
        self.raster = None  # will be free after set_data_info
        self.cube = None
        self.is_sas = False  # STUDYTYP == "Sit-and-stare"
        self.is_full_spectrum = False  # STUDYTYP == "Single Exposure"
        # otherwise data file is raster
        self.x_or_t = ''  # 't' if is_sas else 'x'
        self.fit_params_values = {}
        self.cube_ready_fit = {}
        self.dims = {}  # key: win_key, key2: dimension, value = dimension length
        self.original_cubes = {}  # original cubes dict: {window_key: numpy_cube, ... }
        self.win_info = {}  # {win_key: {{win_info}}, ...}
        self.first_meta = None
        self.wave = {}  # {win_key: {'min': WAVEMIN, 'max': WAVEMAX, 'unit': WAVEUNIT}, ... } # nm
        self.y_fit_bounds = {}  # {win_key: [min, max]} used for fit bars limits
        self.I_unit = ''

    def load_file(self, main, data_path):
        self.main = main
        failed = False
        try:
            self.raster = _read_single_spice_l2_fits(data_path)
        except:
            failed = True

        if failed or self.raster is None:
            Log.p('Failed reading file ' + str(data_path), 'error')
            return False

        for win_key, raster in self.raster.items():
            self.original_cubes[win_key] = np.array(raster.data)
        self.set_data_info()
        self.raster = None  # free
        return True
    
    @property
    def step(self):
        try:
            return float(self.first_meta.get("CDELT1"))
        except:
            return 1

    def lambda_index_to_unit(self, w, lambda_index):  # Angstrom
        return round(lambda_index * (w.wave_max - w.wave_min) / self.get_dim(w.win_key, 'lambda') + w.wave_min, 1)

    def lambda_meter(self, w, lambda_index):  # meter
        return 1e-10 * (lambda_index * (w.wave_max - w.wave_min) / self.get_dim(w.win_key, 'lambda') + w.wave_min)


    def get_study_header_detail(self):
        keywords = ['STUDYTYP', 'STUDYDES', 'descripSTUDY', 'OBS_MODE', 'OBS_TYPE', 'AUTHOR', 'OBS_ID', 'SPIOBSID',
                    'OBS_DESC', 'PURPOSE', 'READMODE', 'TRIGGERD', 'TARGET', 'SOOPNAME', 'SOOPTYPE', 'STP', 'SETFILE',
                    'SETVER', 'APID', 'NRASTERS', 'RASTERNO', 'STUDY_ID', 'MISOSTUD', 'XSTART', 'XPOSURE', 'FOCUSPOS',
                    'NSEGMENT', 'NWIN', 'NWIN_DUM', 'NWIN_INT']
        detail = {}
        for kw in keywords:
            try:
                detail[kw] = str(self.first_meta.get(kw))
            except:  # keyword not found
                pass
        return detail

    def get_win_header_detail(self, win_key):
        keywords = ['MISOWIN', 'WINTABID', 'SLIT_ID', 'SLIT_WID', 'WINSHIFT',
                    'WAVEUNIT', 'WAVEREF', 'WAVEMIN', 'WAVEMAX', 'WINWIDTH', 'BTYPE']
        detail = {}
        for kw in keywords:
            try:
                detail[kw] = str(self.raster[win_key].meta.get(kw))
            except:  # keyword not found
                pass
        return detail
        
    def get_win_info(self, header_list, specific_win):
        for win_key, header in header_list.items():
            if specific_win is None or specific_win == win_key:
                d0 = {'META information': ''}
                d1 = header['meta']
                d2 = {'WCS information': ''}
                d3 = header['wcs']
                d4 = {'NAXIS dims': 'x y ' + Const.lambda_char + ' t'}
                d5 = {'Study details': ''}
                d6 = self.get_study_header_detail()
                if specific_win is not None:
                    d7 = {'Window details': ''}
                    d8 = self.get_win_header_detail(specific_win)
                    return {**d0, **d1, **d2, **d3, **d4, **d5, **d6, **d7, **d8}
                return {**d0, **d1, **d2, **d3, **d4, **d5, **d6}
    
    def get_adjusted_third_D(self, plot):  # according to study step and rescaled lambda
        axis = self.x_or_t
        abscissa_factor = self.main.abscissa_factor(plot.plot_key)
        if plot.plot_key == 'lambda_y':
            axis = 'lambda'
        return self.get_dim(plot.w.win_key, axis) * abscissa_factor
    
    def average1D_values(self, plot, dim, get_integers=False):
        dim_len = self.main.dh.get_dim(plot.w.win_key, dim)
        pos_or_date = ' date' if self.is_sas else ' position'
        option_text = pos_or_date if plot.plot_key == 'lambda_y' else ' wavelength'
        if get_integers:
            divisors = [0]
        else:
            divisors = ['1' + option_text + ' (no average)']
        for i in range(2, dim_len + 1):
            if dim_len % i == 0:
                if get_integers:
                    divisors.append(i)
                else:
                    last_str = ' (the whole dimension)' if i == dim_len else ''
                    divisors.append(str(i) + option_text + 's' + last_str)
        return divisors
    
    def apply_average2D(self, np_2D_slice, kernel_size):
        np_2D_slice = np.nan_to_num(np_2D_slice, 0.)
        min_I = np.nanmin(np_2D_slice)
        if min_I < 0:
            np_2D_slice -= min_I # adding min (because min_I < 0) to get only positive values
        max_I = np.nanmax(np_2D_slice)
        if max_I != 0:
            np_2D_slice = 255. * np_2D_slice / max_I
        kernel = np.ones((kernel_size, kernel_size)) / (kernel_size * kernel_size)
        opencv_result = cv2.filter2D(np_2D_slice, -1, kernel)
        
        # Restore initial values (0-255 was used for opencv interpretation)
        opencv_result = max_I * opencv_result / 255.
        opencv_result += min_I
        #plt_show(opencv_result)
        
        return opencv_result

    @property
    def nb_windows(self):
        return len(self.data_info['win_keys'])
    
    def get_leveled_cube(self, np_cube):
        level_min = self.main.f_menu.applied_levels['min']
        level_max = self.main.f_menu.applied_levels['max']
        level_method = self.main.f_menu.applied_levels['method']

        if level_min is not None:
            c = np_cube

            min_threshold_value = np.nanpercentile(c, level_min)
            max_threshold_value = np.nanpercentile(c, level_max)
            c[c < min_threshold_value] = min_threshold_value
            c[c > max_threshold_value] = max_threshold_value

            if level_method != 'Linear':  # log or sqrt
                # reduce to [0;1]
                min_ = np.nanmin(c)
                c -= min_
                c /= np.nanmax(c) - min_

                a = 1000
                f = np.sqrt if level_method == 'Square root' else np.log10  # neither Linear nor sqrt => log
                c = f(a*c + 1) / f(a + 1)
            return c
        return np_cube

    def copy_original_cube(self, win_key, t_index):
        if self.is_sas:
            np_cube = self.original_cubes[win_key][:, :, :, 0]  # dim(x) == 1, shape is (t, lambda, y)
            np_cube = np.transpose(np_cube, (1, 2, 0))  # shape is (lambda, y, t)
        else:
            np_cube = self.original_cubes[win_key][t_index, :, :, :]  # shape is (lambda, y, x)
        return np.copy(np_cube)  # replacing PlotMap.dc,oc,ac will free the memory for the previous cubes
    
    def update_map_data(self, plot_map, t_index=0):
        win_key = plot_map.w.win_key
        plot_key = plot_map.plot_key
        bin_number = plot_map.bin_number
        average2D_kernel_size = plot_map.average2D_kernel_size
        c = self.copy_original_cube(win_key, t_index)
        
        if bin_number > 0:
            if plot_key == 'x_y':
                c = rebinGabriel(np.nan_to_num(c, True, 0.), (bin_number, 1, 1))
                #c = rebinGabriel(c, (bin_number, 1, 1)) TODO try to put this instead
                c = np.repeat(c, bin_number, axis=0)
            else:  # lambda_y
                c = rebinGabriel(c, (1, 1, bin_number))
                c = np.repeat(c, bin_number, axis=2)
        elif average2D_kernel_size > 0:
            if plot_key == 'x_y':
                for lambda_ in range(self.get_dim(win_key, 'lambda')):
                    c[lambda_] = self.apply_average2D(c[lambda_], average2D_kernel_size)
            else:  # lambda_y
                for x in range(self.get_dim(win_key, 'x')):
                    c[:, :, x] = self.apply_average2D(c[:, :, x], average2D_kernel_size)

        shape = (0, 2, 1)  # for x_y shape is (lambda, x, y)
        if plot_key == 'lambda_y':
            shape = (2, 0, 1)  # for lambda_y shape is (x, lambda, y)
        c = np.transpose(c, shape)

        # Store original cube (with the good shape)
        oc = self.copy_original_cube(win_key, t_index)
        oc = np.transpose(oc, shape)
        plot_map.oc = oc

        # Store averaged cube (without leveling)
        plot_bloc = self.main.get_plot_bloc(plot_map)
        if plot_bloc is not None and plot_key == 'x_y':  # doing it once is enough
            plot_line = plot_bloc['lambda_I']
            plot_line.ac = np.copy(c)

        # Store displayed cube (averaged + leveled)
        c = self.get_leveled_cube(c)
        plot_map.dc = c
        
    def get_lambda_I(self, plot_line, x, y):
        t_index = 0

        if plot_line.ac is None:
            c = self.copy_original_cube(plot_line.w.win_key, t_index)
            c = np.transpose(c, (0, 2, 1))  # shape is (lambda, x, y)
            plot_line.ac = c
        else:
            c = plot_line.ac
        if x is None:
            x = int(self.get_dim(plot_line.w.win_key, 'x') / 2.)
        if y is None:
            y = Const.default_y_index
        np_array = c[:, int(x), int(y)]
        lambda_ = []
        intensities = []  # TODO change to easier numpy manipulation
        for i, intensity in enumerate(np_array):
            if not np.isnan(intensity):
                lambda_.append(i)
                intensities.append(intensity)
        return np.array(lambda_), np.array(intensities)
    
    def init_fit_curves(self, given_win_key=None, t_index=0):
        sas_x_index = 0  # sit and stare
        for win_key, plot_bloc in self.main.global_plots.items():
            if given_win_key == win_key or win_key is None:
                self.fit_params_values[win_key] = {'fit_1': [], 'fit_2': [], 'fit_3': []}
                if self.is_sas:
                    np_cube = np.copy(self.original_cubes[win_key][:, :, :, sas_x_index])  # shape is (t, lambda, y)
                    transposed = np.transpose(np_cube, (0, 2, 1))  # shape is (t, y, lambda) then
                else:
                    np_cube = np.copy(self.original_cubes[win_key][t_index, :, :, :])  # shape is (lambda, y, x)
                    transposed = np.transpose(np_cube, (2, 1, 0))  # shape is (x, y, lambda) then

                self.cube_ready_fit[win_key] = np.nan_to_num(transposed, True, 0.)

    def get_dim(self, win_key, axis):  # axis is x, y, lambda or t
        if win_key not in self.dims:
            self.dims[win_key] = self.get_dims(self.original_cubes[win_key])  # slow, do it once
        return self.dims[win_key][axis]
    
    def get_dims(self, cube):
        return {'x': len(cube[0][0][0]), 'y': len(cube[0][0]), 'lambda': len(cube[0]), 't': len(cube)}

    def get_wavelength_range(self, win_key):
        factor = pow(10, self.wave[win_key]['unit'] - (-10))  # in Angstrom)
        return self.wave[win_key]['min'] * factor, self.wave[win_key]['max'] * factor
        # Angstrom (nm in FITS files)

    def get_meta_str(self, win_key):
        meta = self.raster[win_key].meta
        return {
            'Observatory': meta.observatory,
            'Instrument': meta.instrument,
            'Detector': meta.detector,
            'Spectral Window': meta.spectral_window,
            'Date': meta.date_reference,
            'OBS_ID (SOC Observation ID)': meta.observing_mode_id_solar_orbiter,
            'SPIOBSID (SPICE Observation ID)': meta.spice_observation_id
        }

    def get_wcs(self, win_key):
        wcs_dict = {}
        wcs_str = str(self.raster[win_key].wcs).replace('WCS Keywords\n\n', '')
        for splitted_el in wcs_str.split('\n'):
            key_val = splitted_el.split(':')
            wcs_dict[key_val[0]] = key_val[1]
        return wcs_dict
        
    def set_data_info(self):
        #file_path = full_file_path('solo_L2_spice-w-exp_20220102T131134_V02_100663333-000.fits', data_path)
        
        #print(raster) # cubes
        #print(raster['Full SW 4:1 Focal Lossy']) # one cube
        #print(raster['Full SW 4:1 Focal Lossy'].meta) # Detector, date, window, obsid, ...
        win_keys = list(self.raster.keys())
        header_list = {}
        self.wavelength_ranges = {}
        self.first_meta = None
        for win_key in win_keys:
            curr_meta = self.raster[win_key].meta
            if self.first_meta is None:
                self.first_meta = curr_meta
            header_list[win_key] = {'meta': self.get_meta_str(win_key),
                                     'wcs': self.get_wcs(win_key)}
            self.wave[win_key] = {
                'min': float(curr_meta.get('WAVEMIN')),
                'max': float(curr_meta.get('WAVEMAX')),
                'unit': int(curr_meta.get('WAVEUNIT'))
            }
            self.I_unit = curr_meta.get('BUNIT')
            self.y_fit_bounds[win_key] = [200, 800]  # TODO use Terje's method?
            self.win_info[win_key] = self.get_win_info(header_list, win_key)
        #print(self.raster[first_key].wcs)
        #cube = self.raster[first_key].data
        """for data1 in cube:
            dim1 = (str(len(cube)))
            for data2 in data1:
                dim2 = (str(len(data2)))
                for data3 in data2:
                    dim3 = (str(len(data3)))
                    value = list(data3)[0]
                    print(str(value))"""
        
        #print(len(cube), len(cube[0]), len(cube[0][0]), len(cube[0][0][0]))
        # previous line shows "reversed" NAXIS read in this order:
        # cube is time dimension i.e. cube[0] is the cube for t=0
        # cube[i] is wave dim i.e. cube[i][0] is the square for t=t_i and lambda=lambda_0
        # cube[i][j] is dim y so cube[i][j][0] is a 1-dim list of xes for y=y_0
        # cube[i][j][k] is dim x i.e. cube[i][j][k][0] is the intensity (float) for:
        #   t = t_i
        #   lambda = lambda_j
        #   y = y_k
        #   x = x_0
        
        # Study detail extraction
        to_extract = {'Study name': 'STUDY', 'Author': 'AUTHOR', 'OBS_ID (SOC obs id)': 'OBS_ID',
            'Type (STUDYTYP)': 'STUDYTYP', 'MISO ID (MISOSTUD)': 'MISOSTUD', 'X start (XSTART)': 'XSTART',
            'Exposure time (s) (XPOSURE)': 'XPOSURE', 'Step (CDELT1)': 'CDELT1', 'Number of windows (NWIN)': 'NWIN'}
        study_details = {'Study details': ''}
        for label, fits_key in to_extract.items():
            study_details[label] = str(self.first_meta.get(fits_key))

        self.is_sas = study_details['Type (STUDYTYP)'] == 'Sit-and-stare'
        self.is_full_spectrum = study_details['Type (STUDYTYP)'] == 'Single Exposure'
        self.x_or_t = 't' if self.is_sas else 'x'
                
        """for win_key in win_keys:
            print(self.get_dims(self.original_cubes[win_key]))"""
        self.data_info = {'header_list': header_list, 'win_keys': win_keys,
                          'study_details': study_details}
