import json
from pathlib import Path
from src.capr import CAPR
from src.chatgpt import ChatGPT
from src.framework import Framework

framework = Framework("defects4j")
chatgpt = ChatGPT(model="gpt-3.5-turbo", 
                  api_key_path=Path(__file__).parent.parent / 'openai_api_key.env',
                  cache_folder=Path(__file__).parent / 'data' / 'chatgpt_cache',
                  load_from_cache=True,
                  save_to_cache=True)
capr = CAPR(chatgpt=chatgpt, framework=framework, max_conv_length=3, max_tries=10)

list_of_bugs = ["Lang_1", "Lang_2"]
plausible_patches = {}
repair_cost = {}

results_file = Path(__file__).parent / 'data' / 'results.json'

def print_conversation(json_path):
    with open(json_path, 'r') as file:
        cached_conversation = json.load(file)
        messages = [(message['role'],message['content']) for message in cached_conversation['call']['messages']]
        messages.append(("assistant",cached_conversation['response']['choices'][0]['message']['content']))
    for role, message in messages:
        if role == "assistant":
            print(f'\x1b[32m\'{message}\'\x1b[0m\n')
        else:
            print(message)        
        

def main():
    print_conversation(Path(__file__).parent / 'test' / 'test_capr_cache' / 'attempt_13' / '5_2c6347584959d4fd41e191d2fc459d23.json')
    # for bug_id in list_of_bugs:
    #     bug = framework.reproduce_bug(bug_id)
        
    #     plausible_patches[bug_id], repair_cost[bug_id] = capr.repair(bug=bug)

    # results = [(plausible_patches[bug_id], repair_cost[bug_id]) for bug_id in list_of_bugs]
    # with open(results_file, "w") as file:
    #     file.write(results)

if __name__ == "__main__":
    main()