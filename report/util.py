""" report.util
"""

import os
from .config import config

def console2html(txt):
    """ this is dumb, but doing more would mean requiring
        ansi2html. more requirements means more problems..
    """
    return txt.replace('\n', '<br/>')

# TODO: import this from goulash?
def truncate_file_path(file_name, max_file_components=None):
    max_file_components = max_file_components or config.MAX_FILE_COMPONENTS
    file_parts  = file_name.split(os.path.sep)
    if len(file_parts) > 4:
        file_name = os.path.sep.join(file_parts[-max_file_components:])
    return file_name
