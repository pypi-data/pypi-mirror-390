import time
from ....processing.threads.thread_worker import ThreadWorker


class MakeProcessAvailable(ThreadWorker):
    # "self.objects" is {'win_key': win_key, 'rate': <int in sec>, 'process': 'related_main_attribute'}

    def run(self):
        time.sleep(self.objects['rate'])
        if self.objects['process'] == 'updating_profile':
            self.main.updating_profile[self.objects['win_key']] = False
        elif self.objects['process'] == 'double_click':
            self.main.double_click = False
        elif self.objects['process'] == 'force_third_D':
            self.main.force_third_D = False

        super(MakeProcessAvailable, self).run()
