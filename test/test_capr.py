import unittest
from pathlib import Path
from src.chatgpt import ChatGPT
from src.capr import CAPR
from src.framework import Framework
from prog_params import ProgParams as prog_params
from user_params import UserParams as user_params

class TestCAPR(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.chatgpt_model = prog_params.gpt35_model
        self.chatgpt_api_key = user_params.API_KEY
        self.cache_folder = Path(__file__).parent / 'test_capr_cache'
        self.d4j_path = user_params.D4J_PATH
        self.java_home = user_params.JAVA_HOME
        self.tmp_dir = user_params.TMP_DIR

    def test_init(self):
        chatgpt = ChatGPT(model=self.chatgpt_model, 
                          api_key=self.chatgpt_api_key,
                          cache_folder=self.cache_folder,
                          load_from_cache=True,
                          save_to_cache=True)
        framework = Framework("defects4j", list_of_bugs=[("Chart", [1])], d4j_path=self.d4j_path, java_home=self.java_home, tmp_dir=self.tmp_dir)
        capr = CAPR(chatgpt=chatgpt, framework=framework)
        self.assertIsInstance(capr, CAPR)

    def test_extract_patch_from_response(self):
        chatgpt = ChatGPT(model=self.chatgpt_model, 
                          api_key=self.chatgpt_api_key,
                          cache_folder=self.cache_folder,
                          load_from_cache=True,
                          save_to_cache=True)
        framework = Framework("defects4j", list_of_bugs=None, d4j_path=self.d4j_path, java_home=self.java_home, tmp_dir=self.tmp_dir)
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
                          api_key=self.chatgpt_api_key,
                          cache_folder=self.cache_folder,
                          load_from_cache=True,
                          save_to_cache=True)
        framework = Framework("defects4j", list_of_bugs=None, d4j_path=self.d4j_path, java_home=self.java_home, tmp_dir=self.tmp_dir)
        capr = CAPR(chatgpt=chatgpt, framework=framework)
        
        response_patch_pairs = [
            ("```java\nif (!throwOnNonFiniteDouble && (Double.isNaN(value) || Double.isInfinite(value))) {\n    throw new IOException(\"Numeric values must be finite, but was \" + value);\n}\n``` \nNote: This solution checks if `throwOnNonFiniteDouble` is `false` before throwing the exception to avoid throwing an exception when `throwOnNonFiniteDouble` is `true`.",
             "if (!throwOnNonFiniteDouble && (Double.isNaN(value) || Double.isInfinite(value))) {\n    throw new IOException(\"Numeric values must be finite, but was \" + value);\n}"),
            ("I apologize for the oversight. Here's the corrected patch line:\n\n```java\nif (!lenient && (Double.isNaN(value) || Double.isInfinite(value))) {\n    throw new IllegalArgumentException(\"Numeric values must be finite, but was \" + value);\n}\nreturn this;\n```\n\nIn addition to the check for `lenient` and finite values, we add `return this;` to return the current `JsonWriter` object. This should fix the compilation error.", 
             "if (!lenient && (Double.isNaN(value) || Double.isInfinite(value))) {\n    throw new IllegalArgumentException(\"Numeric values must be finite, but was \" + value);\n}\nreturn this;")
        ]

        for response, patch in response_patch_pairs:
            self.assertEqual(capr.extract_patch_from_response(response), patch)
            
