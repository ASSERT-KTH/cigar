import csv
import json
from pathlib import Path
from src.capr import CAPR
from src.chatgpt import ChatGPT
from src.framework import Framework

# active bugs, based on https://github.com/rjust/defects4j#the-projects
list_of_bugs = [
    ("Chart", [i for i in range(1, 27)]),
    ("Closure", [i for i in range(1, 177) if i != 63 and i != 93]),
    ("Lang", [i for i in range(1, 66) if i != 2]),
    ("Math", [i for i in range(1, 107)]),
    ("Mockito", [i for i in range(1, 39)]), # Failed to reproduce bugs on macOS and Ubuntu
    ("Time", [i for i in range(1, 28) if i != 21])
]

# [TEMPORARY] list of single line bugs
list_of_bugs = [
    ("Lang", [
        6,
        16,
        21,
        24,
        26,
        29,
        33, 
        38, 
        43, 
        51, 
        57, 
        59, 
        61, 
        ])
]

def main():

    max_conv_length = 3
    max_tries = 3
    framework_name = "defects4j"

    framework = Framework(test_framework=framework_name,
                          cache_folder=Path(__file__).parent / 'data' / 'validate_patch_cache')
    chatgpt = ChatGPT(model="gpt-3.5-turbo", 
                    api_key_path=Path(__file__).parent / 'openai_api_key.env',
                    cache_folder=Path(__file__).parent / 'data' / 'chatgpt_cache',
                    load_from_cache=True,
                    save_to_cache=True)
    capr = CAPR(chatgpt=chatgpt, 
                framework=framework, 
                max_conv_length=max_conv_length, 
                max_tries=max_tries)
    
    summary_file_path = Path(__file__).parent / 'data' / 'output' / 'summary.csv'
    plausible_patches_folder = Path(__file__).parent / 'data' / 'output' / 'plausible_patches'
    bug_details_folder = Path(__file__).parent / 'data' / 'output' / 'bug_details'

    fieldnames = ['framework', 'project', 'bug_id',
        'first_plausible_patch_try', 'plausible_patch_count', 'repair_cost', 'conversation_length', 'max_tries', 'comment']
    with open(summary_file_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

    for project, ids in list_of_bugs:
        for bug_id in ids:
            print(f"Reproducing {project}-{bug_id}")
            bug = framework.reproduce_bug(project, bug_id)

            first_plausible_path_try = -1
            plausible_patches = []
            repair_cost = 0
            comment = ""
            blocker = False

            if bug.line_change_count > 2:
                print(f"Skipping {project}-{bug_id} because it has more than 2 line changes")
                comment += "Multiple line change. "
                blocker = True
            if len(bug.test_line) < 2 :
                print(f"Skipping {project}-{bug_id} because test line could not be found")
                comment += "Test line not found. "
                blocker = True
            if "INFILL" not in bug.masked_buggy_code or len(bug.buggy_line) < 2:
                comment += "Buggy line is empty. "
            
            if not blocker:
                print(f"Repairing {project}-{bug_id}")
                first_plausible_path_try, plausible_patches, repair_cost = capr.repair(bug=bug)

            if len(plausible_patches) > 0:
                with open(f'{plausible_patches_folder}/{framework_name}_{project}_{bug_id}_pp.txt', 'w') as f:
                    f.writelines('\n'.join(plausible_patches))
                
            with open(summary_file_path, 'a', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writerow({'framework': framework_name,
                                 'project': project,
                                 'bug_id': bug_id,
                                 'first_plausible_patch_try': first_plausible_path_try, 
                                 'plausible_patch_count': len(plausible_patches),
                                 'repair_cost': repair_cost,
                                 'conversation_length': max_conv_length,
                                 'max_tries': max_tries,
                                 'comment': comment})
                
            with open(f'{bug_details_folder}/{framework_name}_{project}_{bug_id}.txt', 'w') as f:
                vars_object = vars(bug)
                f.write(json.dumps(vars_object, indent=4, sort_keys=True))

if __name__ == "__main__":
    main()