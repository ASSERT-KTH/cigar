import csv
import json
from pathlib import Path
from src.capr import CAPR
from src.chatgpt import ChatGPT
from src.framework import Framework

# based on https://github.com/rjust/defects4j#the-projects
chart_bug_ids = [i for i in range(1, 27)]
closure_bug_ids = [i for i in range(1, 177) if i != 63 and i != 93]
lang_bug_ids = [i for i in range(1, 65) if i != 2]
math_bug_ids = [i for i in range(1, 107)]
mockito_bug_ids = [i for i in range(1, 39)]
time_bug_ids = [i for i in range(1, 27) if i != 21]

list_of_bugs = [
    # ("Chart", chart_bug_ids),
    # ("Closure", closure_bug_ids),
    ("Lang", lang_bug_ids),
    # ("Math", math_bug_ids),
    # ("Mockito", mockito_bug_ids), # Failed to reproduce bugs on macOS and Ubuntu
    # ("Time", time_bug_ids)
]


def main():

    max_conv_length = 3
    max_tries = 10
    framework_name = "defects4j"
    # temperature defaults to 1
    # sample count defaults to 1

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

    fieldnames = ['framework', 'project', 'bug_id',
        'first_plausible_patch_try', 'plausible_patch_count', 'repair_cost', 'conversation_length', 'max_tries', 'comment']
    with open(summary_file_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

    for project, ids in list_of_bugs:
        for bug_id in ids:
            print(f"Reproducing {project}-{bug_id}")
            bug = framework.reproduce_bug(project, bug_id)

            if bug.line_change_count > 2:
                print(f"Skipping {project}-{bug_id} because it has more than 2 line changes")
                with open(summary_file_path, 'a', newline='') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writerow({'framework': framework_name,
                                     'project': project,
                                     'bug_id': bug_id,
                                     'first_plausible_patch_try': -1, 
                                     'plausible_patch_count': 0,
                                     'repair_cost': 0,
                                     'conversation_length': max_conv_length,
                                     'max_tries': max_tries,
                                     'comment': "SKIP: multiple line changes"})
            else:
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
                                     'comment': ""})


if __name__ == "__main__":
    main()