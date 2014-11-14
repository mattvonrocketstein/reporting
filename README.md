[about](#about) | [installation](#installation) | [usage](#usage) | [testing](#testing) |

<a name="about"/>
ABOUT
=====
The report module defines "report", a smarter version of the "print" builtin with features for colorizing output and inspecting the context from which it was called.  In addition to printing whatever message you pass to it `report()` will show the function, file, class, and object that called the report function.  This makes it much more useful as a tool for debugging.

<a name="installation"/>
INSTALLATION
============
From pypi:

```shell
  $ pip install reporting
```

Latest development version:

```shell
  $ git clone https://github.com/mattvonrocketstein/reporting.git
  $ cd reporting
  $ python setup.py install
```

<a name="usage"/>
USAGE
=====

```shell
  >>> from report import report
  >>> report("some message here")
  <ipython-input-27-f3d65c300782> --  <??>.<module> -- test
  >>> def function_name(x):
  ... report("hello world")
  >>> f(x)
   <ipython-input-28-50e1d4686e91> --  <??>.function_name -- testing
```

<a name="testing"/>
TESTING
=======

```shell
  $ cd reporting
  $ tox
```
