import unittest
from pathlib import Path
from src.chatgpt import ChatGPT
from src.capr import CAPR
from src.framework import Framework

class TestCAPR(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.chatgpt_model = "gpt-3.5-turbo"
        self.chatgpt_api_key_path = Path(__file__).parent.parent / 'openai_api_key.env'
        self.cache_folder = Path(__file__).parent / 'test_capr_cache'

    def test_init(self):
        chatgpt = ChatGPT(model=self.chatgpt_model, 
                          api_key_path=self.chatgpt_api_key_path,
                          cache_folder=self.cache_folder,
                          load_from_cache=True,
                          save_to_cache=True)
        framework = Framework("defects4j")
        capr = CAPR(chatgpt=chatgpt, framework=framework, max_conv_length=3, max_tries=10)
        self.assertIsInstance(capr, CAPR)

    # @unittest.skip("Skipping until construct_initial_prompt and validate_patch are working")
    def test_repair(self):
        chatgpt = ChatGPT(model=self.chatgpt_model, 
                          api_key_path=self.chatgpt_api_key_path,
                          cache_folder=self.cache_folder / 'attempt_12',
                          load_from_cache=True,
                          save_to_cache=True)
        framework = Framework("defects4j")
        capr = CAPR(chatgpt=chatgpt, framework=framework, max_conv_length=3, max_tries=6)

        d4j_bug = {"project": "Gson", "bug_id": 15}

        bug = framework.reproduce_bug(d4j_bug)

        plausable_patches, cost_of_repair_attempt = capr.repair(bug)
        self.assertIsInstance(plausable_patches, list)
        self.assertIsInstance(cost_of_repair_attempt, int)
