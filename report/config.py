""" report.config
"""

import sys

class BaseConfig(dict):
    """ move to goulash """
    def __init__(self, *args, **kargs):
        if args:
            err=('if arguments are provided there should be '
                 'exactly one and it should be a dictionary')
            assert len(args)==1 and isinstance(args[0], dict), err
            dct = args[0]
        else:
            dct = kargs
        for k,v in dct.items():
            setattr(self, k, v)

class Config(BaseConfig):
    """ """
    # let's not work too hard if there is no one
    # to notice all the color.  note that stdout
    # should NOT be a tty when pipes are used,
    # which prevents color-codes from cluttering
    # up "python foo.py > log.txt" style invocations
    USING_TTY = sys.stdout.isatty()
    MAX_FILE_COMPONENTS = 4

config = Config()
