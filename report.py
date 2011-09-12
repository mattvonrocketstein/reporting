""" report.py
"""

"""
import logging

LOGGERS = {}
# create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
#formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)

# 'application' code
logger.debug('debug message')
logger.info('info message')
logger.warn('warn message')
logger.error('error message')
logger.critical('critical message')

"""
import os
import sys
import inspect

import pygments
from pygments import highlight
from pygments.lexers import PythonLexer, PythonTracebackLexer
from pygments.formatters import HtmlFormatter,Terminal256Formatter
from pygments.console import colorize as console_color

plex  = PythonLexer()
tblex = PythonTracebackLexer()
hfom  = HtmlFormatter()
hfom2 = HtmlFormatter(cssclass="autumn")
colorize  = lambda code: highlight(code, plex, hfom)
colorize2 = lambda code: highlight(code, plex, hfom2)

class console:
    """ from the pygments code--

        dark_colors  = ["black", "darkred", "darkgreen", "brown", "darkblue",
            "purple", "teal", "lightgray"]
        light_colors = ["darkgray", "red", "green", "yellow", "blue",
            "fuchsia", "turquoise", "white"]

        codes["darkteal"]   = codes["turquoise"]
        codes["darkyellow"] = codes["brown"]
        codes["fuscia"]     = codes["fuchsia"]
        codes["white"]      = codes["bold"]
    """
    def __getattr__(self, name):
        if name.startswith('_'):
            raise AttributeError
        def func(string, _print=False):
            z = console_color(name,string)
            if _print:
                print z
            return z
        return func

    def vertical_space(self):
        print

    @staticmethod
    def colortb(string):
        return highlight(string, tblex, Terminal256Formatter())

    @staticmethod
    def color(string):
        return highlight(string, plex, Terminal256Formatter()).strip()

    @staticmethod
    def draw_line(msg='', length=80, display=True):
        if msg and not msg.startswith(' '): msg = ' '+msg
        if msg and not msg.endswith(' '):   msg = msg+' '
        rlength = length - len(msg)
        out = '-' * (rlength/2)
        out+= msg + out
        out = console.red(out)
        if display:
            print out
        return out
console = console()

def whoami():
    """ gives information about the caller """
    return inspect.stack()[1][3]

def getcaller(level=2):
    x = inspect.stack()[level]
    frame = x[0]
    file_name = x[1]
    flocals = frame.f_locals
    func_name = x[3]
    file = file_name
    self = flocals.get('self',None)
    kls  = self and self.__class__
    kls_func = getattr(kls, func_name, None)
    if type(kls_func)==property:
        func = kls_func
    else:
        try: func = self and getattr(self,func_name)
        except AttributeError: func = func_name+'[nested]'
    return dict(file=file_name,
                kls=kls,
                self=self,
                func=func,
                func_name=func_name)

def whosdaddy():
    """ displays information about the caller's caller """
    # if self is a named argument in the locals, print
    # the class name, otherwise admit that we don't know
    caller_info = getcaller(3)
    kls         = caller_info['kls']
    file_name   = caller_info['file']
    func_name   = caller_info['func_name']
    header      = (kls and kls.__name__) or '<??>'
    header      = header + '.' + func_name
    file_parts  = file_name.split(os.path.sep)
    if len(file_parts) > 4:
        file_name = os.path.sep.join(file_parts[-4:])
    return ' + ' + console.darkblue(file_name) + ' --  ' + console.blue(header)

def report(*args, **kargs):
    """ reporting mechanism with inspection and colorized output """
    stream = kargs.pop('stream', sys.stdout)
    header = kargs.pop('header', '')
    header=whosdaddy();
    print header

    if len(args)==1:
            _args = str(args[0])
            # if kargs appears to be a formatting string for the one and only
            # argument, then use it as such and set kargs to empty so it wont
            # be printed
            if len([ k for k in kargs if '{'+k+'}' in _args]) == len(kargs):
                _args = _args.format(**kargs)
                kargs = {}
            _args = console.darkteal(_args.strip())
    else:
            _args = 'args=' + console.color(str(args)).strip()
    _args = _args + '\n' if _args else _args
    _kargs =  console.color(str(kargs)) if kargs else ''
    _kargs = _kargs +'\n' if _kargs else _kargs
    sep = '    '
    stream.write( sep + _args + sep + _kargs)

def getReporter(**unused):
    """ TODO: return a partial function """
    return report

report = getReporter()
