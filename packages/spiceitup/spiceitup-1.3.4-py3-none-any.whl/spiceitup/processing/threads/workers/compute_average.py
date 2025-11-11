from ....utils.internal_utils import *
from ....processing.fit import *
from ....processing.threads.thread_worker import ThreadWorker


class ComputeAverage(ThreadWorker):
    # "self.objects" is a plot_map

    def update_progress(self, val):  # does += val
        self.th.progress_signal.emit(self.th.rt.get_pf_dict(val))

    def run(self):
        plot = self.objects
        refresh_map = True

        if plot.averaging == '1D' and plot.bin_choice > 0:
            plot.average2D_choice = 0
            refresh_map = plot.c_average2D.currentIndex() == 0
            plot.c_average2D.setCurrentIndex(0)

        elif plot.averaging == '2D' and plot.average2D_choice > 0:
            plot.bin_choice = 0
            refresh_map = plot.c_average1D.currentIndex() == 0
            plot.c_average1D.setCurrentIndex(0)

        if refresh_map:  # above the setCurrentIndex will trigger this thread again and will go here anyway
            if plot.plot_key == 'x_y' or plot.plot_key == 'lambda_y':
                self.main.dh.update_map_data(plot)
            self.update_progress(50)
            self.th.plots_to_refresh.append({'th': self.th, 'plot': plot})
            plot_bloc = self.main.get_plot_bloc(plot)
            self.th.plots_to_refresh.append({'th': self.th, 'plot': plot_bloc['lambda_I']})

        super(ComputeAverage, self).run()
