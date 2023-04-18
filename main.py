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

# based on https://github.com/rjust/defects4j#the-projects
chart_bug_ids = [i for i in range(1, 27)]
closure_bug_ids = [i for i in range(1, 177) if i != 63 and i != 93]
lang_bug_ids = [i for i in range(1, 65) if i != 2]
math_bug_ids = [i for i in range(1, 107)]
mockito_bug_ids = [i for i in range(1, 39)]
time_bug_ids = [i for i in range(1, 27) if i != 21]

list_of_bugs = [
    ("Chart", chart_bug_ids),
    ("Closure", closure_bug_ids),
    ("Lang", lang_bug_ids),
    ("Math", math_bug_ids),
    # ("Mockito", mockito_bug_ids), # Failed to reproduce bugs on macOS and Ubuntu
    ("Time", time_bug_ids)
]

plausible_patches = {}
repair_cost = {}
        

def main():
    for project, ids in list_of_bugs:
        for bug_id in ids:
            print(f"Reproducing {project}-{bug_id}")
            bug = framework.reproduce_bug(project, bug_id)

            if bug.line_change_count > 2:
                print(f"Skipping {project}-{bug_id} because it has more than 2 line changes")
            else:
                print(f"Repairing {project}-{bug_id}")
                # plausible_patches[bug_id], repair_cost[bug_id] = capr.repair(bug=bug)

if __name__ == "__main__":
    main()