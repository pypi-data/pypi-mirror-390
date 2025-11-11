from ....utils.internal_utils import *
from ....logs.log import Log
from ....processing.threads.thread_worker import ThreadWorker
from ....settings.const import Const

class OutOfSync(ThreadWorker):
    # "self.objects" is out of sync duration (exec after n secs)
    # Usage: RunThread('OutOfSync', self.main, 0.2[, 'Thread name with progress bar'])
    # Instead of 0.2 give -1 to wait as long as other threads run
    # Instead of 0.2 give -2 to wait as long as thread is not interrupted (see RunningThread.do_interrupt)

    def update_progress(self, val):  # does += val
        self.th.progress_signal.emit(self.th.rt.get_pf_dict(val))

    def run(self):
        t = self.objects
        if t == -1:
            for i in range(10 * Const.max_pending):
                if self.main.nb_running_threads <= 1:
                    break
                #Log.p('OutOfSync (t = -1): Waiting because nb_running_thread = ' + str(self.main.nb_running_threads) + ' <= 1')
                time.sleep(0.1)  # e.g. wait for plots to be ready
        elif t == -2:
            self.update_progress(1)
            while self.th.do_interrupt is False:
                time.sleep(0.1)
            Log.p('Interrupting OutOfSync (t = -2)...')
        else:
            time.sleep(t)  # e.g. allows to close the "browse file" window
        super(OutOfSync, self).run()
