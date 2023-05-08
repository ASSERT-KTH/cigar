import json
from pathlib import Path


def print_call(json_path):
    with open(json_path, 'r') as file:
        cached_conversation = json.load(file)
        messages = [(message['role'],message['content']) for message in cached_conversation['call']['messages']]
        messages.append(("assistant",cached_conversation['response']['choices'][0]['message']['content']))
    for role, message in messages:
        if role == "system":
            print(f'\x1b[33m\'{message}\'\x1b[0m\n')
        if role == "assistant":
            print(f'\x1b[32m\'{message}\'\x1b[0m\n')
        else:
            print(message)        

# when main is called, expect path as argument
if __name__ == "__main__":
    import sys
    json_path = Path(sys.argv[1])
    print_call(json_path)
