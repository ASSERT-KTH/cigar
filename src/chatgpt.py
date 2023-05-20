import json
import openai
import hashlib
from pathlib import Path

class ChatGPT(object):
    def __init__(self, model="gpt-3.5-turbo", api_key=None,
                 cache_folder=None, load_from_cache=True, save_to_cache=True):
        self.model = model
        if api_key is not None:
            openai.api_key = api_key
        self.cache_folder = cache_folder
        self.load_from_cache = load_from_cache
        self.save_to_cache = save_to_cache

    def call(self, prompt, num_of_samples=1, prefix=None):

        response = None
        call_params = self.get_call_params(prompt, num_of_samples)
        cache_file_path = self.get_cache_file_path(prompt, num_of_samples, prefix)

        if self.load_from_cache and self.cache_folder is not None:
            if Path(cache_file_path).is_file():
                with open(cache_file_path, "r") as file:
                    json_to_load = json.load(file)
                    response = json_to_load['response']

        if response is None:
            response = openai.ChatCompletion.create(**call_params)

        if self.save_to_cache and self.cache_folder is not None:
            with open(cache_file_path, "w") as file:
                json_to_save = self.get_json_to_save(call_params, response)
                file.write(json.dumps(json_to_save, indent=4, sort_keys=True))
            
        response_message = response['choices'][0]['message']['content']
        response_token_usage = response['usage']['total_tokens']
        return (response_message, response_token_usage)
    
    def get_call_params(self, prompt, num_of_samples=1):
        return {
            "model": self.model,
            "messages": prompt,
            "n": num_of_samples,
            "temperature": 1,
            "top_p": 1,
        }

    def get_call_hash(self, prompt, num_of_samples=1):
        call_params = self.get_call_params(prompt, num_of_samples=num_of_samples)
        return hashlib.md5(str(call_params).encode('utf-8')).hexdigest()
    
    def get_cache_file_path(self, prompt, num_of_samples=1, prefix=None):
        call_hash = self.get_call_hash(prompt, num_of_samples)
        if prefix is not None:
            return f"{self.cache_folder}/{prefix}_{call_hash}.json"
        return f"{self.cache_folder}/{call_hash}.json"
    
    def get_json_to_save(self, call_params, response):
        return {
            "call": call_params,
            "response": response
        }
