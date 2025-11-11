from ....utils.internal_utils import *
from ....logs.log import Log
from ....processing.threads.thread_worker import ThreadWorker


class LoadPlotMap(ThreadWorker):
    # "self.objects" is {'plot_map': PlotMap, 'np_data': filled_once_thread_is_done}

    def run(self):
        plot_map = self.objects
        plot_key = plot_map.plot_key
        if plot_key == 'x_y' or plot_key == 'lambda_y':
            self.main.dh.update_map_data(plot_map)
        elif 'fit' in plot_key:
            pass
        else:
            Log.p('Image constructor got a wrong plot_key, x_y, lambda_y, fit_1, fit_2 or fit_3 ' +
                  'are authorized.', 'error')
            self.th.plot_map_np_data = None
            super(LoadPlotMap, self).run()
        super(LoadPlotMap, self).run()
