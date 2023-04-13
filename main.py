from pathlib import Path
from src.capr import CAPR
from src.chatgpt import ChatGPT
from defects4j.d4j import Defects4J

framework = Defects4J()
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

def main():
    for bug_id in list_of_bugs:
        bug = framework.reproduce_bug(bug_id)
        
        plausible_patches[bug_id], repair_cost[bug_id] = capr.repair(bug=bug)

    results = [(plausible_patches[bug_id], repair_cost[bug_id]) for bug_id in list_of_bugs]
    with open(results_file, "w") as file:
        file.write(results)

if __name__ == "__main__":
    main()