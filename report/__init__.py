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

from .version import __version__

plex  = PythonLexer()
jlex  = JavascriptLexer()
tblex = PythonTracebackLexer()
hfom  = HtmlFormatter()
hfom2 = HtmlFormatter(cssclass="autumn")
highlight = copy.copy(highlight)
ROW_LEN_CACHE = dict(timestamp=None, stdout_row_length=None)
highlight.javascript = lambda code: highlight(code, jlex, Terminal256Formatter())
highlight.python = lambda code: highlight(code, plex, Terminal256Formatter())

class config(object):
    """ """
    MAX_FILE_COMPONENTS = 4

if not sys.stdout.isatty():
    # let's not work too hard if there is no one
    # to notice all the color.  note that stdout
    # should NOT be a tty when pipes are used,
    # which prevents color-codes from cluttering
    # up "python foo.py > log.txt" style invocations
    console_color = lambda name, string: string
    stdout_row_length = lambda: 80
else:
    from pygments.console import colorize as console_color
    def stdout_row_length():
        """ returns the number of cols in the display.
            this is cached for CACHE_LENGTH amount of time,
            but after that it's recomputed.  this allows for
            terminal windows that are getting resized to behave
            as expected and do some intelligent wrapping
        """
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

def console2html(txt):
    return txt.replace('\n', '<br/>')

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
    html = staticmethod(console2html)

    def __getattr__(self, name):
        if name.startswith('_'):
            raise AttributeError
        def func(string, _print=False):
            z = console_color(name, string)
            if _print:
                print z
            return z
        return func

    @staticmethod
    def colortb(string):
        return highlight(string, tblex, Terminal256Formatter())

    if sys.stdout.isatty():
        def color(string):
            return highlight(string, plex, Terminal256Formatter()).strip()
    else:
        color = lambda string: string
    color = staticmethod(color)

    @staticmethod
    def draw_line(msg='', length=80, display=True):
        if msg and not msg.startswith(' '): msg = ' '+msg
        if msg and not msg.endswith(' '):   msg = msg+' '
        rlength = length - len(msg)
        out  = '-' * (rlength/2)
        out += msg + out
        out = console.red(out)
        if display:
            print out
        return out

# TODO: import this from goulash
def truncate_file_path(file_name):
    file_parts  = file_name.split(os.path.sep)
    if len(file_parts) > 4:
        file_name = os.path.sep.join(file_parts[-config.MAX_FILE_COMPONENTS:])
    return file_name


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
    file_name = truncate_file_path(file_name)
    return file_name, header

def _report(*args, **kargs):
    """ reporting mechanism with inspection and colorized output """
    stream = kargs.pop('stream', sys.stdout)
    header = kargs.pop('header', '')
    use_header = ""
    fname, caller = frames_back(kargs.pop('frames_back', 3))
    colored_header = ' ' + console.darkblue(fname) + ' --  ' + console.blue(caller)
    extra_length = len(' + '+' --  ') #ugh
    header_length = len(fname+caller)+extra_length
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
            if (len(_args+' -- ') + header_length) < stdout_row_length():
                use_header = colored_header + ' -- ' + console.darkteal(_args)
                _args = ''
            else:
                _args = '  ' + console.darkteal(_args)
                use_header = colored_header
    else:
        s = StringIO()
        args_as_text = pprint(args, s)
        args_as_text = s.getvalue()
        _args = 'args=' + console.color(args_as_text).strip() + '\n'
    print use_header
    _args = _args + '\n' if _args else _args
    _kargs =  console.color(str(kargs)) if kargs else ''
    _kargs = _kargs +'\n' if _kargs else _kargs
    sep = ' '
    output= sep + _args + sep + _kargs
    stream.write(output.strip()+'\n')
    stream.flush()

def getReporter(**unused):
    """ TODO: return a partial function """
    return _report

class Reporter(object):
    """ syntactic sugar for reporting """
    def __init__(self, label=u'>>'):
        self.label = label

    def __getattr__(self, label):
        return self.__class__('.'.join([self.label, label]))

    def _report(self,msg):
        def mycolorize(txt):
            """ """
            # .format() is not used because KeyError might happen
            # when using report(msg+str(some_dictionary))
            return txt.replace('{red}',console_codes['red']).replace(
                '{normal}', console_codes['reset'])
        print mycolorize('{red}' + self.label + '{normal}: ' + msg)

    def _warn(self, msg):
        warning = getattr(self, 'WARNING')
        return warning(msg)
    warn = _warn

    def __call__(self, msg):
        return self._report(msg)

simple = Reporter()
report = getReporter()
report.console = console
report.highlight = highlight
console = console()
