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

    @unittest.skip("End-to-end test, takes long to run, resolves Gson-15 bug.")
    def test_repair_gson_15(self):
        chatgpt = ChatGPT(model=self.chatgpt_model, 
                          api_key_path=self.chatgpt_api_key_path,
                          cache_folder=self.cache_folder / 'attempt_14',
                          load_from_cache=True,
                          save_to_cache=True)
        framework = Framework("defects4j")
        capr = CAPR(chatgpt=chatgpt, framework=framework, max_conv_length=3, max_tries=6)

        d4j_bug = {"project": "Gson", "bug_id": 15}

        bug = framework.reproduce_bug(d4j_bug)

        plausable_patches, cost_of_repair_attempt = capr.repair(bug)
        self.assertIsInstance(plausable_patches, list)
        self.assertIsInstance(cost_of_repair_attempt, int)

    @unittest.skip("End-to-end test, takes long to run, resolves Lang-16 bug.")
    def test_repair_lang_16(self):
        chatgpt = ChatGPT(model=self.chatgpt_model, 
                          api_key_path=self.chatgpt_api_key_path,
                          cache_folder=self.cache_folder / 'attempt_16',
                          load_from_cache=True,
                          save_to_cache=True)
        framework = Framework("defects4j")
        capr = CAPR(chatgpt=chatgpt, framework=framework, max_conv_length=3, max_tries=12)

        d4j_bug = {"project": "Lang", "bug_id": 16}

        bug = framework.reproduce_bug(d4j_bug)

        plausable_patches, cost_of_repair_attempt = capr.repair(bug)
        self.assertIsInstance(plausable_patches, list)
        self.assertIsInstance(cost_of_repair_attempt, int)


    def test_extract_patch_from_response(self):
        chatgpt = ChatGPT(model=self.chatgpt_model, 
                          api_key_path=self.chatgpt_api_key_path,
                          cache_folder=self.cache_folder,
                          load_from_cache=True,
                          save_to_cache=True)
        framework = Framework("defects4j")
        capr = CAPR(chatgpt=chatgpt, framework=framework, max_conv_length=3, max_tries=10)
        
        response_patch_pairs = [
            ("Alternative fix line:\n```java\nif (Double.isNaN(value) || Double.isInfinite(value)) {\n```", 
             "if (Double.isNaN(value) || Double.isInfinite(value)) {"),
            ("Alternative fix line:\n\n```java\nif (!Double.isFinite(value)) {\n```", 
             "if (!Double.isFinite(value)) {"),
            ("```java\nif (!throwOnNonFiniteDouble && (Double.isNaN(value) || Double.isInfinite(value))) {\n    throw new IOException(\"Numeric values must be finite, but was \" + value);\n}\n``` \nNote: This solution checks if `throwOnNonFiniteDouble` is `false` before throwing the exception to avoid throwing an exception when `throwOnNonFiniteDouble` is `true`.",
             "if (!throwOnNonFiniteDouble && (Double.isNaN(value) || Double.isInfinite(value))) {"),
            ("```java\nif (Double.isNaN(value) || Double.isInfinite(value)) {\n    throw new IOException(\"Numeric values must be finite, but was \" + value);\n}\n``` \nNote: Since `JsonWriter` implements `Closeable` and `Flushable`, it is appropriate to throw an `IOException`.",
             "if (Double.isNaN(value) || Double.isInfinite(value)) {"),
            ("Apologies for the confusion. Here's the correct patch line:\n\n```java\nif (!lenient && (Double.isNaN(value) || Double.isInfinite(value))) {\n    throw new IllegalArgumentException(\"Numeric values must be finite, but was \" + value);\n}\n``` \n\nThis line includes a check for the `lenient` flag, which is missing in the previous version. If `lenient` is set to true, non-finite doubles will be allowed. Otherwise, an exception will be thrown.", 
             "if (!lenient && (Double.isNaN(value) || Double.isInfinite(value))) {"),
            ("I apologize for the oversight. Here's the corrected patch line:\n\n```java\nif (!lenient && (Double.isNaN(value) || Double.isInfinite(value))) {\n    throw new IllegalArgumentException(\"Numeric values must be finite, but was \" + value);\n}\nreturn this;\n```\n\nIn addition to the check for `lenient` and finite values, we add `return this;` to return the current `JsonWriter` object. This should fix the compilation error.", 
             "if (!lenient && (Double.isNaN(value) || Double.isInfinite(value))) {")
        ]

        for response, patch in response_patch_pairs:
            self.assertEqual(capr.extract_patch_from_response(response), patch)
            
