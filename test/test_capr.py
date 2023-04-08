from pathlib import Path
import unittest
from chatgpt import ChatGPT

from src.capr import Capr

class TestCapr(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.chatgpt_model = "gpt-3.5-turbo"
        self.chatgpt_api_key_path = Path(__file__).parent.parent / 'openai_api_key.env'
        self.cache_folder = Path(__file__).parent / 'test_chatgpt_cache'

    def test_init(self):
        initial_prompt = None
        chatgpt = None
        max_conv_length = None
        max_tries = None
        alt_instruct = None
        capr = Capr(initial_prompt, chatgpt, max_conv_length, max_tries, alt_instruct)
        self.assertIsInstance(capr, Capr)

    def test_attempt_to_repair(self):
        initial_prompt = "TODO: Initial patch prompt"
        chatgpt = ChatGPT(model=self.chatgpt_model, 
                          api_key_path=self.chatgpt_api_key_path,
                          cache_folder=self.cache_folder,
                          load_from_cache=True,
                          save_to_cache=True)
        max_conv_length = 3
        max_tries = 10
        alt_instruct = "TODO: Plausable patch prompt"
        capr = Capr(initial_prompt, chatgpt, max_conv_length, max_tries, alt_instruct)
        plausable_patches, cost_of_repair_attempt = capr.attempt_to_repair(chat)
        self.assertIsInstance(plausable_patches, list)
        self.assertIsInstance(cost_of_repair_attempt, int)