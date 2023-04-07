import unittest
import hashlib
from unittest.mock import patch
from src.chatgpt import ChatGPT
from pathlib import Path

class TestChatGPT(unittest.TestCase):
    # def __init__(self, methodName: str = "runTest") -> None:
    #     super().__init__(methodName)

    def test_init(self):
        chatgpt = ChatGPT()
        self.assertIsInstance(chatgpt, ChatGPT)

    def test_mocked_openai_call(self):

        chatgpt = ChatGPT(load_from_cache=False, save_to_cache=False)
        prompt = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"},
            {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
            {"role": "user", "content": "Where was it played?"}
        ]
        response = {
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

        with patch('src.chatgpt.openai.ChatCompletion.create') as mock_create:
            mock_create.return_value = response
            response_message, _ = chatgpt.call(prompt)
            mock_create.assert_called_once()

        cached_response_message = "The 2020 World Series was played in Arlington, Texas at the Globe Life Field, which was the new home stadium for the Texas Rangers."
        self.assertEqual(response_message, cached_response_message)
            
    def test_that_mocked_openai_call_creates_cache_file(self):

        chatgpt = ChatGPT(cache_folder=Path(__file__).parent.parent / 'data' / 'chatgpt_cache',
                          load_from_cache=False, save_to_cache=True)
        prompt = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"},
            {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
            {"role": "user", "content": "Where was it played?"}
        ]
        response = {
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

        with patch('src.chatgpt.openai.ChatCompletion.create') as mock_create:
            mock_create.return_value = response
            response_message, _ = chatgpt.call(prompt)

        call_hash = chatgpt.get_call_hash(prompt=prompt)
        path_to_file = Path(__file__).parent.parent / 'data' / 'chatgpt_cache' / f'{call_hash}.json'
        path = Path(path_to_file)
        self.assertTrue(path.is_file())      

    def test_loading_cached_openai_call(self):
        chatgpt = ChatGPT(cache_folder=Path(__file__).parent.parent / 'data' / 'chatgpt_cache',
                          load_from_cache=True, save_to_cache=False)
        prompt = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"},
            {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
            {"role": "user", "content": "Where was it played?"}
        ]

        cached_response_message = "The 2020 World Series was played in Arlington, Texas at the Globe Life Field, which was the new home stadium for the Texas Rangers."
        response_message, _ = chatgpt.call(prompt)

        self.assertEqual(response_message, cached_response_message)

    def test_saving_and_loading_cached_openai_call(self):
        chatgpt = ChatGPT(cache_folder=Path(__file__).parent.parent / 'data' / 'chatgpt_cache',
                          load_from_cache=True, save_to_cache=True)
        prompt = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"},
            {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
            {"role": "user", "content": "Where was it played?"}
        ]
        response = {
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
        
        with patch('src.chatgpt.openai.ChatCompletion.create') as mock_create:
            mock_create.return_value = response
            response_message, _ = chatgpt.call(prompt)

        cached_response_message = "The 2020 World Series was played in Arlington, Texas at the Globe Life Field, which was the new home stadium for the Texas Rangers."

        self.assertEqual(response_message, cached_response_message)

        call_hash = chatgpt.get_call_hash(prompt=prompt)
        path_to_file = Path(__file__).parent.parent / 'data' / 'chatgpt_cache' / f'{call_hash}.json'
        path = Path(path_to_file)
        self.assertTrue(path.is_file())   

    def test_openai_call(self):
        chatgpt = ChatGPT(load_from_cache=False, save_to_cache=False)
        prompt = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"},
            {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
            {"role": "user", "content": "Where was it played?"}
        ]
        response_message, response_token_usage = chatgpt.call(prompt)
        self.assertIsInstance(response_message, str)
        self.assertIsInstance(response_token_usage, int)
        self.assertGreater(response_token_usage, 0)