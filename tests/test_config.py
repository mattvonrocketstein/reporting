"""test_config
"""
import unittest
from report import Config

class TestConfig(unittest.TestCase):
    def test_config(self):
        default_config = Config()
        custom = Config(dict(USING_TTY=not default_config.USING_TTY))
        self.assertNotEqual(default_config.USING_TTY, custom.USING_TTY)
