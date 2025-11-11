#!/usr/bin/env python3
from PyQt5.QtCore import *
import numpy as np
from ...logs.log import Log
# /!\ Keep these lines, it's used by globals()
from ...processing.threads.workers.compute_average import ComputeAverage
from ...processing.threads.workers.generate_fit_maps import GenerateFitMaps
from ...processing.threads.workers.update_levels import UpdateLevels
from ...processing.threads.workers.update_profile import UpdateProfile
from ...processing.threads.workers.make_process_available import MakeProcessAvailable
from ...processing.threads.workers.out_of_sync import OutOfSync
from ...processing.threads.workers.load_plot_map import LoadPlotMap
# ----


class RunThread:
    main = None
    running_thread = None  # RunningThread instance
    worker_class_name = None
    thread_name = None
    end_func = None
    end_func_args = None
    do_display_progress = False
    progress_id = 0
    # id of progress bar in footer, use then function in footer.py that contains id in the name
    # (not index! which is just the nth line constantly changing)
    progress_val = 0

    def __init__(self, worker_class_name, main, objects=None, thread_name=None,
                 end_func=None, end_func_args=None, with_cancel=True):
        # end_func() has main as arg and end_func_args if not None
        """
        progress_func must be None or a static method: myfunc(pf_dict)
        pf_dict = {'main': self.main, 'other_var': 'something', ...}
        (defined in workers before emetting progress_signal)
        end_func has rt as argument (recover rt.main and rt.end_func_args)
        """
        self.main = main
        self.thread_name = thread_name
        self.end_func = end_func
        self.end_func_args = end_func_args
        self.do_display_progress = thread_name is not None
        self.worker_class_name = worker_class_name
        if self.do_display_progress:
            self.progress_id = main.f_footer.create_progress_line(self, thread_name, with_cancel)
            self.progress_val = 0

        main.update_nb_threads(1, True)

        Worker = globals()[worker_class_name]
        rth = RunningThread(self)
        worker = Worker(rth, main, objects)
        rth.connect_signals()

        worker.moveToThread(rth)
        rth.started.connect(worker.run)
        worker.finished.connect(rth.quit)
        worker.finished.connect(worker.deleteLater)
        rth.finished.connect(rth.deleteLater)
        rth.start()
        self.running_thread = rth
        main.ths.append(rth)
        main.thws.append(worker)
        main.rts.append(self)

    def interrupt(self):
        self.running_thread.do_interrupt = True
        self.main.f_footer.interrupt_progress_line_by_id(self.progress_id)

    def add_end_func_arg(self, key, val):  # /!\ only handled if end_func_args is a dict
        if self.end_func_args is None:
            self.end_func_args = {key: val}
        elif type(self.end_func_args).__name__ == 'dict':
            self.end_func_args[key] = val
        else:
            Log.p('Try to add_end_func_arg() whereas end_func_args is neither a dict nor None (' +
                  str(type(self.end_func_args)) + ').', 'error')

    def force_success_interruption(self):  # typically for worker OutOfSync t = -2
        self.progress_func(self.get_pf_dict('done'))
        self.running_thread.do_interrupt = True

    def get_pf_dict(self, val):
        if val == 'done':
            self.progress_val = 100
        else:
            self.progress_val += val
            if self.progress_val > 99:
                self.progress_val = 99  # avoid setting it done, because time is then needed to refresh plots
        return {'main': self.main, 'progress_id': self.progress_id, 'val': self.progress_val}

    @staticmethod
    def progress_func(pf_dict):  # keys: 'main', 'progress_id' and 'val'
        pf_dict['main'].f_footer.update_progress_line_by_id(pf_dict['progress_id'], round(pf_dict['val']))

class RunningThread(QThread):
    # self.th in worker classes (see workers/ folder content)

    rt = None  # RunThread instance
    progress_signal = pyqtSignal(object)  # pf_dict
    end_thread_signal = pyqtSignal()
    plots_to_refresh = []  # list of {'th': th, 'plot': PlotMap/PlotLine}
    fit_maps_data = None
    do_interrupt = False  # if True, run() will interrupt asap
    
    def __init__(self, rt, parent=None):
        super(RunningThread, self).__init__(parent)
        self.rt = rt

    def end_thread(self):
        for ptr in self.plots_to_refresh:
            if ptr['th'] == self:  # checks if this is executed from the good worker
                ptr['plot'].refresh()
        self.plots_to_refresh = []

        if self.fit_maps_data is not None:
            xy_map = self.fit_maps_data['xy_map']
            win_key = xy_map.w.win_key
            plot_bloc = self.fit_maps_data['plot_bloc']
            for fit_i in range(1, 4):
                plot = plot_bloc['fit_' + str(fit_i)]
                plot.dc = np.array(self.rt.main.dh.fit_params_values[win_key][plot.plot_key])
                plot.apply_image_data()
                plot.iv.autoLevels()
                plot.iv.autoRange()

        if type(self.rt.end_func).__name__ == 'function':
            self.rt.end_func(self.rt)  # use rt.end_func_args in the called static method to get other args

        if self.rt.do_display_progress and not self.do_interrupt:
            RunThread.progress_func(self.rt.get_pf_dict('done'))
        self.rt.main.update_nb_threads(-1, True)
        
    def connect_signals(self):
        if self.rt.do_display_progress:
            self.progress_signal.connect(RunThread.progress_func)
        self.end_thread_signal.connect(self.end_thread)
