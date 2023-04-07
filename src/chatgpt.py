import json
import openai
import hashlib
from pathlib import Path

class ChatGPT(object):
    def __init__(self, model="gpt-3.5-turbo", cache_folder=None, load_from_cache=True, save_to_cache=True):
        self.model = model
        self.cache_folder = cache_folder
        self.load_from_cache = load_from_cache
        self.save_to_cache = save_to_cache

    def call(self, prompt):

        response = None
        call_params = self.get_call_params(prompt)
        cache_file_path = self.get_cache_file_path(prompt)

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
    
    def get_call_params(self, prompt):
        return {
            "model": self.model,
            "messages": prompt
        }

    def get_call_hash(self, prompt):
        call_params = self.get_call_params(prompt)
        return hashlib.md5(str(call_params).encode('utf-8')).hexdigest()
    
    def get_cache_file_path(self, prompt):
        call_hash = self.get_call_hash(prompt)
        return f"{self.cache_folder}/{call_hash}.json"
    
    def get_json_to_save(self, call_params, response):
        return {
            "call": call_params,
            "response": response
        }
