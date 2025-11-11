#!/usr/bin/env python3

from datetime import datetime
from ..settings.const import Const

from ..utils.internal_utils import get_ms


class Log:

    @staticmethod
    def p(*msgs, msg_type='info'):
        """Prints in log"""
        prefix = 'INFO'
        if msg_type == 'warn':
            prefix = 'WARNING'
        elif msg_type == 'error':
            prefix = 'ERROR'
        
        today_dt = datetime.now()
        today_str = today_dt.strftime(Const.date_format)

        try:
            with open(Const.log_file, 'a') as f:
                for msg in msgs:
                    f.write(today_str + ' ' + prefix + ': ' + str(msg) + '\n')
        except PermissionError:
            print('Permission denined when appening in ' + Const.log_file)


    @staticmethod
    def p_ms(msg, first_time_ms=0):
        """Prints current time in milliseconds in log file.
        A first_time_ms can be removed in order to investigate more easily the time
        latency between instructions"""
        Log.p(str(get_ms() - first_time_ms) + ': ' + msg)


    @staticmethod
    def p_duration(first_time_ms):
        Log.p('Duration since first time: ' + str(get_ms() - first_time_ms) + ' ms')
