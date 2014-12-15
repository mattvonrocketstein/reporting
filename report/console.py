""" report.console
"""

import copy
from pygments import highlight
from pygments.lexers import JavascriptLexer, PythonLexer, PythonTracebackLexer
from pygments.formatters import HtmlFormatter, Terminal256Formatter
from pygments.console import codes as console_codes
from pygments.console import colorize as _console_color

from .util import console2html
from .config import Config

plex  = PythonLexer()
tblex = PythonTracebackLexer()
highlight = copy.copy(highlight)
highlight.javascript = lambda code: highlight(code, jlex, Terminal256Formatter())
highlight.python = lambda code: highlight(code, plex, Terminal256Formatter())
jlex  = JavascriptLexer()
hfom  = HtmlFormatter()
hfom2 = HtmlFormatter(cssclass="autumn")

class Console(object):
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

    def __init__(self, config=None):
        self.config = Config() if config is None else config

    def __getattr__(self, name):
        if name.startswith('_'):
            raise AttributeError
        if self.config.USING_TTY:
            def func(string, _print=False):
                z = console_color(name, string, self.config)
                if _print:
                    print z
                return z
        else:
            def func(string, _print=False):
                if _print:
                    print string
                return string
        return func

    def colortb(self, string):
        if self.config.USING_TTY:
            return highlight(string, tblex, Terminal256Formatter())
        else:
            return string

    def color(self, string):
        if self.config.USING_TTY:
            return highlight(string, plex, Terminal256Formatter()).strip()
        else:
            return string

    def draw_line(self, msg='', length=80, display=True):
        if msg and not msg.startswith(' '): msg = ' '+msg
        if msg and not msg.endswith(' '):   msg = msg+' '
        rlength = length - len(msg)
        out  = '-' * (rlength/2)
        out += msg + out
        out = self.red(out)
        if display:
            print out
        return out

def console_color(name, string, config):
    if config.USING_TTY:
        return _console_color(name, string)
    else:
        return string
