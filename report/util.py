""" report.util
"""

import os
from report.config import config
from datetime import datetime, timedelta

ROW_LEN_CACHE = dict(timestamp=None, stdout_row_length=None)

# TODO: move this to goulash?
def truncate_file_path(file_name, max_file_components=None):
    max_file_components = max_file_components or config.MAX_FILE_COMPONENTS
    file_parts  = file_name.split(os.path.sep)
    if len(file_parts) > 4:
        file_name = os.path.sep.join(file_parts[-max_file_components:])
    return file_name

def stdout_row_length(config):
    """ returns the number of cols in the display.
        this is cached for CACHE_LENGTH amount of time,
        but after that it's recomputed.  this allows for
        terminal windows that are getting resized to behave
        as expected and do some intelligent wrapping
    """
    if not config.USING_TTY:
        return 80
    if ROW_LEN_CACHE['stdout_row_length'] is None or \
       ROW_LEN_CACHE['timestamp'] < (datetime.now()-timedelta(seconds=10)):
        try:
            cols, rows = os.popen('stty size', 'r').read().split()
            rows = int(rows)
        except:
            rows = 80
        ROW_LEN_CACHE['stdout_row_length'] = int(rows)
        ROW_LEN_CACHE['timestamp'] = datetime.now()
    return ROW_LEN_CACHE['stdout_row_length']
