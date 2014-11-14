""" test_all
"""
import sys
import unittest
from StringIO import StringIO
from contextlib import contextmanager

from report import config, report, truncate_file_path

from pyparsing import (
    Literal, Word, Combine, Optional,
    Suppress, nums, delimitedList, oneOf, alphas)

ESC = Literal('\x1b')
integer = Word(nums)
escapeSeq = Combine(
    ESC + '[' + \
    Optional(delimitedList(integer,';')) + \
    oneOf(list(alphas)))
uncolor = lambda s : Suppress(escapeSeq).transformString(s)

TEST_MSG = "testing"

def function_name(a,b,c):
    report(TEST_MSG)

class MyClass(object):
    def method(self,a,b,c):
        report(TEST_MSG)
    @staticmethod
    def static_method(a, b, c):
        report(TEST_MSG)

class Tests(unittest.TestCase):
    def setUp(self):
        self.fxn = function_name
        self.kls = MyClass()
        new_out, new_err = StringIO(), StringIO()
        self.old_out, self.old_err = sys.stdout, sys.stderr
        sys.stdout, sys.stderr = new_out, new_err
        self.out = new_out
        self.err = new_err

    def tearDown(self):
        sys.stdout, sys.stderr = self.old_out, self.old_err

    def get_output(self):
        return uncolor(self.out.getvalue().strip())

    def assertOutputContains(self, x, err=None):
        output = self.get_output()
        err = err or "{0} not in {1}".format(x,output)
        self.assertTrue(x in output, err)

    def assertEndsWith(self, x, err=None):
        output = self.get_output()
        err = err or output
        self.assertTrue(output.endswith(x), err)

    def assertStartsWith(self, x, err=None):
        output = self.get_output()
        err = err or output
        self.assertTrue(output.startswith(x), err)

    def test_function(self):
        self.fxn(1, 2, 3)
        self.assertOutputContains(self.fxn.__name__)
        self.assertEndsWith(TEST_MSG)

    def test_method(self):
        self.kls.method(1,2,3)
        output = self.get_output()
        self.assertOutputContains(
            self.kls.__class__.__name__+'.'+self.kls.method.__name__)
        self.assertEndsWith(TEST_MSG)
        self.assertStartsWith(
            truncate_file_path(__file__))

    def test_static_method(self):
        self.kls.static_method(1,2,3)
        output = self.get_output()
        # frame info for staticmethod does not include class info
        self.assertOutputContains('<??>.static_method')
