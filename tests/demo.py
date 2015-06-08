""" demo
"""
from report import report

def module_level_function():
    report("hello module!")

class Object(object):
    def instance_method(self):
        report("hello instance method!")
