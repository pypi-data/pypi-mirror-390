import numpy as np
from scipy.interpolate import interp1d

from ....processing.fit import *
from ....logs.log import Log
from ....processing.threads.thread_worker import ThreadWorker
import pyqtgraph as pg


class UpdateProfile(ThreadWorker):
    # "self.objects" is {'plot_line', 'x_index', 'y_index'}

    def run(self):
        try:  # developers: check errors in debug.log
            plot_line = self.objects['plot_line']
            plot_bloc = self.main.get_plot_bloc(plot_line)  # /!\ None on first load

            x_index = self.objects['x_index']
            y_index = self.objects['y_index']
            if x_index is None:  # is not first load
                x_index = plot_bloc['lambda_y'].third_D_value
                y_index = plot_bloc['lambda_y'].y_value

            plot_line.q_label.setText('I(' + self.main.dh.x_or_t + ' = ' + str(x_index) + \
                                      ', y = ' + str(y_index) + ', ' + Const.lambda_char + ') ' + self.main.dh.I_unit)

            win_key = plot_line.w.win_key
            fit_params = []
            hist_data = []
            fit_I = []
            lambda_, I = self.main.dh.get_lambda_I(plot_line, x_index, y_index)
            # lambda_ = np.linspace(0, len(I) - 1, len(I), True, False, int)
            lambda_plus_one = np.append(lambda_, lambda_[-1] + 1)
            hist_data = [lambda_plus_one - 0.5, I]

            if win_key not in self.main.nb_available_bin or self.main.nb_available_bin[win_key] >= Const.min_bins_to_fit:
                offset_b_min, offset_b_max = plot_line.get_K_bounds()
                fit_bounds, fit_params, fit_I = get_gaussian_fit(lambda_, I, offset_b_min, offset_b_max, plot_line.q_footer_label)

                plot_line.min_intensity = min(np.min(I), np.min(fit_I))
                plot_line.max_intensity = max(np.max(I), np.max(fit_I))

            if len(fit_params) > 0:  # fit exists
                fgauss = interp1d(lambda_, fit_I, 'quadratic')

                # Compute chi2
                chi2 = 0.
                for i in range(len(lambda_)):
                    if fit_I[i] != 0:
                        chi2 += (I[i] - fit_I[i])**2 / fit_I[i]
                chi2 /= 3  # number of parameter - 1

                # Improve fit resolution
                lambda_extended = np.linspace(lambda_[0], lambda_[-1], len(lambda_) * Const.fit_resolution)
                fit_I = fgauss(lambda_extended)
                fit_data = [lambda_extended, fit_I]

                self.th.rt.add_end_func_arg('profile_data', {
                    'plot_line': plot_line,
                    'hist_data': hist_data,
                    'fit_data': fit_data,
                    'fit_params': fit_params,
                    'chi2': round(chi2, Const.chi2_digits)
                })
            else:
                self.th.rt.add_end_func_arg('profile_data', {
                    'plot_line': plot_line,
                    'hist_data': hist_data,
                    'fit_data': [],
                    'fit_params': [],
                    'chi2': 0
                })
        except Exception as e:
            Log.p('UpdateProfile failed! ' + str(e), 'error')
            pass

        super(UpdateProfile, self).run()
