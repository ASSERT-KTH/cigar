import unittest
from unittest.mock import patch
from src.chatgpt import ChatGPT
from pathlib import Path

class TestChatGPT(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.api_key_path = Path(__file__).parent.parent / 'openai_api_key.env'
        self.test_cache_path = Path(__file__).parent / 'test_chatgpt_cache'
        self.mocked_prompt = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"},
            {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
            {"role": "user", "content": "Where was it played?"}
        ]
        self.live_prompt = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"}
        ]
        self.test_response = {
            "id": "chatcmpl-6p9XYPYSTTRi0xEviKjjilqrWU2Ve",
            "object": "chat.completion",
            "created": 1677649420,
            "model": "gpt-3.5-turbo",
            "usage": {"prompt_tokens": 56, "completion_tokens": 31, "total_tokens": 87},
            "choices": [
                {
                "message": {
                    "role": "assistant",
                    "content": "The 2020 World Series was played in Arlington, Texas at the Globe Life Field, which was the new home stadium for the Texas Rangers."},
                "finish_reason": "stop",
                "index": 0
                }
            ]
        }
        self.test_response_message = "The 2020 World Series was played in Arlington, Texas at the Globe Life Field, which was the new home stadium for the Texas Rangers."

    def test_init(self):
        chatgpt = ChatGPT()
        self.assertIsInstance(chatgpt, ChatGPT)

    def test_mocked_openai_call(self):

        chatgpt = ChatGPT(load_from_cache=False, save_to_cache=False)
        prompt = self.mocked_prompt
        mocked_response = self.test_response

        with patch('src.chatgpt.openai.ChatCompletion.create') as mock_create:
            mock_create.return_value = mocked_response
            response_message, _ = chatgpt.call(prompt)
            mock_create.assert_called_once()

        self.assertEqual(response_message, self.test_response_message)
            
    def test_that_mocked_openai_call_creates_cache_file(self):

        chatgpt = ChatGPT(cache_folder=self.test_cache_path, load_from_cache=False, save_to_cache=True)
        prompt = self.mocked_prompt
        mocked_response = self.test_response

        with patch('src.chatgpt.openai.ChatCompletion.create') as mock_create:
            mock_create.return_value = mocked_response
            response_message, _ = chatgpt.call(prompt)

        path_to_file = chatgpt.get_cache_file_path(prompt=prompt)
        path = Path(path_to_file)
        self.assertTrue(path.is_file())      

    def test_loading_cached_openai_call(self):
        chatgpt = ChatGPT(cache_folder=self.test_cache_path, load_from_cache=True, save_to_cache=False)
        prompt = self.mocked_prompt

        response_message, _ = chatgpt.call(prompt)

        self.assertEqual(response_message, self.test_response_message)

    def test_saving_and_loading_cached_openai_call(self):
        chatgpt = ChatGPT(cache_folder=self.test_cache_path, load_from_cache=True, save_to_cache=True)
        prompt = self.mocked_prompt
        
        response_message, _ = chatgpt.call(prompt)

        self.assertEqual(response_message, self.test_response_message)

        path_to_file = chatgpt.get_cache_file_path(prompt=prompt)
        path = Path(path_to_file)
        self.assertTrue(path.is_file())   

    @unittest.skip("Skipping test_openai_call because it requires an OpenAI API key")
    def test_openai_call(self):
        chatgpt = ChatGPT(api_key_path=self.api_key_path, 
                          cache_folder=self.test_cache_path, 
                          load_from_cache=False, 
                          save_to_cache=True)
        prompt = self.live_prompt
        response_message, response_token_usage = chatgpt.call(prompt)
        self.assertIsInstance(response_message, str)
        self.assertIsInstance(response_token_usage, int)
        self.assertGreater(response_token_usage, 0)