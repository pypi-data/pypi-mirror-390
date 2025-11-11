from scipy.constants import speed_of_light

from ....processing.fit import *
from ....logs.log import Log
from ....processing.threads.thread_worker import ThreadWorker


class GenerateFitMaps(ThreadWorker):
    # "self.objects" is xy_map (PlotMap instance)

    def update_progress(self, val):  # does += val
        self.th.progress_signal.emit(self.th.rt.get_pf_dict(val))

    def run(self):
        plot_bloc = self.objects
        xy_map = plot_bloc['x_y']
        win_key = xy_map.w.win_key
        if self.main.dh.is_sas:
            len_x = self.main.dh.get_dim(win_key, 't')
        else:
            len_x = self.main.dh.get_dim(win_key, 'x')
        max_y = self.main.dh.get_dim(win_key, 'y')
        x_range = range(len_x)
        y_range = range(xy_map.fit_maps_y_min, min(xy_map.fit_maps_y_max, max_y))
        len_y = len(list(y_range))
        lambda_range = range(self.main.dh.get_dim(win_key, 'lambda'))
        self.main.dh.init_fit_curves(win_key)
        offset_b_min, offset_b_max = plot_bloc['lambda_I'].get_K_bounds()
        for x_i in x_range:
            param_xes = [[], [], []]
            for y_i in y_range:
                if self.th.do_interrupt:
                    Log.p('Interrupting GenerateFitMaps...')
                    super(GenerateFitMaps, self).run()
                    return
                intensities = self.main.dh.cube_ready_fit[win_key][x_i, y_i, :]  # if sas, x_i is time
                #intensities = intensities[~np.isnan(intensities)]
                fit_bounds, fit_params, fit_I = get_gaussian_fit(lambda_range, intensities, offset_b_min, offset_b_max)
                param_xes[0].append(fit_params[0])
                param_xes[1].append(fit_params[1])
                param_xes[2].append(fit_params[2])
                self.update_progress(100 / (len_x * len_y))
            self.main.dh.fit_params_values[win_key]['fit_1'].append(param_xes[0])
            self.main.dh.fit_params_values[win_key]['fit_2'].append(param_xes[1])
            self.main.dh.fit_params_values[win_key]['fit_3'].append(param_xes[2])

        self.main.dh.fit_params_values[win_key]['fit_1'] = np.array(self.main.dh.fit_params_values[win_key]['fit_1'])
        self.main.dh.fit_params_values[win_key]['fit_2'] = np.array(self.main.dh.fit_params_values[win_key]['fit_2'])
        self.main.dh.fit_params_values[win_key]['fit_3'] = np.array(self.main.dh.fit_params_values[win_key]['fit_3'])

        # Convert lambda_max to velocity
        lambda_0 = self.main.dh.lambda_meter(xy_map.w, np.median(self.main.dh.fit_params_values[win_key]['fit_2']))
        lambda_mes = self.main.dh.lambda_meter(xy_map.w, self.main.dh.fit_params_values[win_key]['fit_2'])
        self.main.dh.fit_params_values[win_key]['fit_2'] = (lambda_mes - lambda_0) * speed_of_light / lambda_0 / 1000.

        # Convert sigma to velocity
        sigma_mes = self.main.dh.lambda_meter(xy_map.w, self.main.dh.fit_params_values[win_key]['fit_3'])
        self.main.dh.fit_params_values[win_key]['fit_3'] = (sigma_mes - lambda_0) * speed_of_light / lambda_0 / 1000.
        # review above 5641
        self.th.fit_maps_data = {
            'xy_map': xy_map,
            'plot_bloc': self.main.global_plots[win_key]
        }

        super(GenerateFitMaps, self).run()
