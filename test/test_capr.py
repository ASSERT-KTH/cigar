import unittest

from src.capr import Capr

class TestCapr(unittest.TestCase):
    def test_init(self):
        initial_prompt = None
        chatgpt = None
        max_conv_length = None
        max_tries = None
        alt_instruct = None
        capr = Capr(initial_prompt, chatgpt, max_conv_length, max_tries, alt_instruct)
        self.assertIsInstance(capr, Capr)