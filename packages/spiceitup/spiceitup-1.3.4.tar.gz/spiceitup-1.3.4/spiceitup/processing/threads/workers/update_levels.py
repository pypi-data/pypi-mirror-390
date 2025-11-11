from ....logs.log import Log
from ....processing.threads.thread_worker import ThreadWorker


class UpdateLevels(ThreadWorker):
    # "self.objects" is a win_key (is False for global levels)

    def update_progress(self, val):  # does += val
        self.th.progress_signal.emit(self.th.rt.get_pf_dict(val))

    def run(self):
        win_key = self.objects
        is_global = win_key is False
        nb_windows = len(self.main.global_plots.items()) if is_global else 1

        for curr_win_key, plot_bloc in self.main.global_plots.items():
            if is_global or win_key == curr_win_key:  # global levels or specific to 1 window
                nb_plots = len(plot_bloc.keys())
                for plot_key, plot in plot_bloc.items():
                    if self.th.do_interrupt:
                        Log.p('Interrupting UpdateLevels thread...')
                        self.th.plots_to_refresh = []  # cancel refreshing previous maps
                        super(UpdateLevels, self).run()
                        return
                    self.update_progress(100. / (nb_windows * nb_plots))
                    refresh_it = True
                    if plot.plot_key == 'x_y' or plot.plot_key == 'lambda_y':
                        self.main.dh.update_map_data(plot)
                    elif plot.plot_key == 'fit_1':
                        pass # do not update data but do refresh the (leveled) map
                    else:
                        refresh_it = False

                    if refresh_it:
                        self.th.plots_to_refresh.append({'th': self.th, 'plot': plot})

        super(UpdateLevels, self).run()
