""" test_config
"""
import unittest

from report import Config

class TestConfig(unittest.TestCase):
    def test_config(self):
        default_config = Config()
        custom = Config(dict(USING_TTY=not default_config.USING_TTY))
        self.assertNotEqual(default_config.USING_TTY, custom.USING_TTY)

    def test_config_dict_arg(self):
        config = Config(dict(a='b',c='d'))
        self.assertEqual(config.a, 'b')

    def test_config_kargs(self):
        config = Config(a='b',c='d')
        self.assertEqual(config.a, 'b')
