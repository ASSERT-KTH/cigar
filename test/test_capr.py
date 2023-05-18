import unittest
from pathlib import Path
from src.chatgpt import ChatGPT
from src.capr import CAPR
from src.framework import Framework

class TestCAPR(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.chatgpt_model = "gpt-3.5-turbo-0301"
        self.chatgpt_api_key_path = Path(__file__).parent.parent / 'openai_api_key.env'
        self.cache_folder = Path(__file__).parent / 'test_capr_cache'

    def test_init(self):
        chatgpt = ChatGPT(model=self.chatgpt_model, 
                          api_key_path=self.chatgpt_api_key_path,
                          cache_folder=self.cache_folder,
                          load_from_cache=True,
                          save_to_cache=True)
        framework = Framework("defects4j", list_of_bugs=[("Chart", [1])])
        capr = CAPR(chatgpt=chatgpt, framework=framework)
        self.assertIsInstance(capr, CAPR)

    def test_extract_patch_from_response(self):
        chatgpt = ChatGPT(model=self.chatgpt_model, 
                          api_key_path=self.chatgpt_api_key_path,
                          cache_folder=self.cache_folder,
                          load_from_cache=True,
                          save_to_cache=True)
        framework = Framework("defects4j", list_of_bugs=None)
        capr = CAPR(chatgpt=chatgpt, framework=framework)
        
        response_patch_pairs = [
            ("Alternative fix line:\n```java\nif (Double.isNaN(value) || Double.isInfinite(value)) {\n```", 
             "if (Double.isNaN(value) || Double.isInfinite(value)) {"),
            ("Alternative fix line:\n\n```java\nif (!Double.isFinite(value)) {\n```", 
             "if (!Double.isFinite(value)) {"),
        ]

        for response, patch in response_patch_pairs:
            self.assertEqual(capr.extract_patch_from_response(response), patch)

    def test_extract_patch_from_response_with_multiple_lines(self):
        chatgpt = ChatGPT(model=self.chatgpt_model, 
                          api_key_path=self.chatgpt_api_key_path,
                          cache_folder=self.cache_folder,
                          load_from_cache=True,
                          save_to_cache=True)
        framework = Framework("defects4j", list_of_bugs=None)
        capr = CAPR(chatgpt=chatgpt, framework=framework)
        
        response_patch_pairs = [
            ("```java\nif (!throwOnNonFiniteDouble && (Double.isNaN(value) || Double.isInfinite(value))) {\n    throw new IOException(\"Numeric values must be finite, but was \" + value);\n}\n``` \nNote: This solution checks if `throwOnNonFiniteDouble` is `false` before throwing the exception to avoid throwing an exception when `throwOnNonFiniteDouble` is `true`.",
             "if (!throwOnNonFiniteDouble && (Double.isNaN(value) || Double.isInfinite(value))) {\n    throw new IOException(\"Numeric values must be finite, but was \" + value);\n}"),
            ("I apologize for the oversight. Here's the corrected patch line:\n\n```java\nif (!lenient && (Double.isNaN(value) || Double.isInfinite(value))) {\n    throw new IllegalArgumentException(\"Numeric values must be finite, but was \" + value);\n}\nreturn this;\n```\n\nIn addition to the check for `lenient` and finite values, we add `return this;` to return the current `JsonWriter` object. This should fix the compilation error.", 
             "if (!lenient && (Double.isNaN(value) || Double.isInfinite(value))) {\n    throw new IllegalArgumentException(\"Numeric values must be finite, but was \" + value);\n}\nreturn this;")
        ]

        for response, patch in response_patch_pairs:
            self.assertEqual(capr.extract_patch_from_response(response), patch)
            
