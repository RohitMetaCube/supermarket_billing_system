import re
import logging
import traceback


class OneLineExceptionFormatter(logging.Formatter):
    def formatException(self, exc_info):
        tb = re.sub("\n", "\t", traceback.format_exc(exc_info[2]))
        result = tb
        return result  # or format into one line however you want to

    def format(self, record):
        s = super(OneLineExceptionFormatter, self).format(record)
        s = s.replace('\n', '\t')
        return s
