import json
import os
from pathlib import Path


def print_calls(chatgpt_cache_path):
    cache_file_names = os.listdir(chatgpt_cache_path)
    current_index = 0

    while True:
        print_call(f"{chatgpt_cache_path}/{cache_file_names[current_index]}")
        inp = input(f"\nCurrent cache file: {cache_file_names[current_index]}\nPress b or p to go back, any other key to go forward, q to quit:\n")
        if inp == "q":
            break
        elif inp == "b" or inp == "p":
            current_index = (current_index-1) % len(cache_file_names)
        else:
            current_index = (current_index+1) % len(cache_file_names)
        


def print_call(json_path):    
    with open(json_path, 'r') as file:
        cached_conversation = json.load(file)
        messages = [(message['role'],message['content']) for message in cached_conversation['call']['messages']]
        messages.append(("assistant",cached_conversation['response']['choices'][0]['message']['content']))
    print()
    for role, message in messages:
        if role == "system":
            print(f'\x1b[33m{message}\x1b[0m\n')
        elif role == "assistant":
            print(f'\x1b[32m{message}\x1b[0m\n')
        else:
            print(message)        


if __name__ == "__main__":
    chatgpt_cache_path = Path(__file__).parent.parent / 'data' / 'chatgpt_cache'
    print_calls(chatgpt_cache_path)