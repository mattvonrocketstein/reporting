""" report
"""
import os
import sys
import copy
import inspect
from pprint import pprint
from StringIO import StringIO
from datetime import datetime, timedelta

from pygments import highlight
from pygments.lexers import JavascriptLexer, PythonLexer, PythonTracebackLexer
from pygments.formatters import HtmlFormatter, Terminal256Formatter
from pygments.console import codes as console_codes


from goulash._inspect import getcaller
from .console import Console
from .version import __version__
from .util import truncate_file_path, console2html
from .config import Config



ROW_LEN_CACHE = dict(timestamp=None, stdout_row_length=None)

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


def frames_back(N=3):
    """ displays information about the caller's caller """
    # if self is a named argument in the locals, use
    # the class name, otherwise admit that we don't know
    caller_info = getcaller(N)
    kls         = caller_info['class']
    file_name   = caller_info['file']
    func_name   = caller_info['func_name']
    header      = (kls and kls.__name__) or '<??>'
    header      = header + '.' + func_name
    return file_name, header

class Report(object):

    def __init__(self, config=None, console=None):
        self.config = Config() if config is None else config
        self.console = Console(self.config) if not console else console

    def __call__(self, *args, **kargs):
        """ reporting mechanism with inspection and colorized output """
        stream = kargs.pop('stream', sys.stdout)
        header = kargs.pop('header', '')
        use_header = header
        fname, caller = frames_back(kargs.pop('frames_back', 3))
        fname = truncate_file_path(fname, self.config.MAX_FILE_COMPONENTS)
        colored_header = ' ' + self.console.darkblue(fname) + ' --  ' + self.console.blue(caller)
        extra_length = len(' + '+' --  ') #ugh
        header_length = len(fname+caller) + extra_length
        if len(args)==1:
            _args = str(args[0])
            # if kargs appears to be a formatting string for the one and only
            # argument, then use it as such and set kargs to empty so it wont
            # be printed
            if len([ k for k in kargs if '{'+k+'}' in _args]) == len(kargs):
                try:
                    _args = _args.format(**kargs)
                except KeyError:
                    pass
                kargs = {}
            _args = _args.strip()
            # whenever terminal is wide enough to show both,
            # mash up the header with the other output
            if (len(_args+' -- ') + header_length) < stdout_row_length(self.config):
                use_header = colored_header + ' -- ' + self.console.darkteal(_args)
                _args = ''
            else:
                _args = '  ' + self.console.darkteal(_args)
                use_header = colored_header
        else:
            s = StringIO()
            args_as_text = pprint(args, s)
            args_as_text = s.getvalue()
            _args = 'args=' + self.console.color(args_as_text).strip() + '\n'
        print use_header
        _args = _args + '\n' if _args else _args
        _kargs =  self.console.color(str(kargs)) if kargs else ''
        _kargs = _kargs +'\n' if _kargs else _kargs
        sep = ' '
        output= sep + _args + sep + _kargs
        stream.write(output.strip()+'\n')
        stream.flush()

class Reporter(object):
    """ syntactic sugar for reporting """
    def __init__(self, label=u'>>', config=None, console=None):
        self.label = label
        self.config = Config() if config is None else config
        self.console = Console(self.config) if not console else console
        self.report = Report(self.config, self.console)

    def __getattr__(self, label):
        return self.__class__(
            '.'.join([self.label, label]),
            config = self.config, console=self.console)

    def _report(self, msg):

        # .format() is not used because KeyError might happen
        # when using report(msg+str(some_dictionary))
        red = console_codes['red']
        normal = console_codes['reset']
        hdr = self.label.replace('{red}', red).replace('{normal}', normal)
        #self.report(hdr +": "+ msg, frames_back=4)
        print (red + self.label + normal+': ' + msg)

    def _warn(self, msg):
        warning = getattr(self, 'WARNING')
        return warning(msg)
    warn = _warn

    def __call__(self, msg):
        return self._report(msg)

console = Console()#config)
#simple = Reporter(config, console)
report = Report()#config, console)
report.highlight = highlight
