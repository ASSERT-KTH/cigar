import csv
import json
from pathlib import Path
from src.capr import CAPR
from src.chatgpt import ChatGPT
from src.framework import Framework

def main():
    max_tries = 1
    n_shot_count = 1
    max_conv_length = 3
    framework_name = "defects4j"

    framework = Framework(test_framework=framework_name,
                          list_of_bugs= [("Chart", [i for i in range(1, 27)]),
                                         ("Closure", [i for i in range(1, 177) if i != 63 and i != 93]),
                                         ("Lang", [i for i in range(1, 66) if i != 2]),
                                         ("Math", [i for i in range(1, 107)]),
                                         ("Mockito", [i for i in range(1, 39)]), # Failed to reproduce bugs on macOS and Ubuntu
                                         ("Time", [i for i in range(1, 28) if i != 21])],
                          validate_patch_cache_folder=Path(__file__).parent / 'data' / 'validate_patch_cache',
                          n_shot_cache_folder=Path(__file__).parent / 'data' / 'n_shot_cache')
    chatgpt = ChatGPT(model="gpt-3.5-turbo-0301", 
                    api_key_path=Path(__file__).parent / 'openai_api_key.env',
                    cache_folder=Path(__file__).parent / 'data' / 'chatgpt_cache',
                    load_from_cache=True,
                    save_to_cache=True)
    capr = CAPR(chatgpt=chatgpt, 
                framework=framework)
    
    summary_file_path = Path(__file__).parent / 'data' / 'output' / 'summary.csv'
    plausible_patches_folder = Path(__file__).parent / 'data' / 'output' / 'plausible_patches'
    bug_details_folder = Path(__file__).parent / 'data' / 'output' / 'bug_details'

    # list_of_bugs= [("Time", [4, 5, 15, 16, 18, 19, 20])] # Bugs fixed by the authors
    list_of_bugs= [("Time", [19])] # Bugs fixed by the authors

    fieldnames = ['framework', 'project', 'bug_id', 'bug_type',
                  'SL_ppc', 'SL_rc', 'SL_fppt', 'SL_fppcl', 'SL_mts',
                  'SH_ppc', 'SH_rc', 'SH_fppt', 'SH_fppcl', 'SH_mts',
                  'SF_ppc', 'SF_rc', 'SF_fppt', 'SF_fppcl', 'SF_mts',
                  'max_conv_length', 'comment']
    with open(summary_file_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

    for project, ids in list_of_bugs:
        for bug_id in ids:
            print(f"Reproducing {project}-{bug_id}")
            bug = framework.reproduce_bug(project, bug_id)

            row = {key: "" for key in fieldnames}
            row['framework'] = framework_name
            row['project'] = project
            row['bug_id'] = bug_id
            row['bug_type'] = bug.bug_type
            row['max_conv_length'] = max_conv_length

            if bug.bug_type != "OT":
                # for mode in ['SL', 'SH', 'SF']:
                for mode in ['SL', 'SH']:
                    if mode in bug.bug_type:
                        print(f"Repairing {project}-{bug_id} ({mode})")
                        plausible_patches, repair_cost, first_plausible_patch_try, first_plausible_patch_conv_len = capr.repair(bug=bug, 
                                                                                                                                mode=mode, 
                                                                                                                                n_shot_count=n_shot_count,
                                                                                                                                stop_after_first_plausible_patch=True,
                                                                                                                                max_tries=max_tries,
                                                                                                                                max_conv_length=max_conv_length)

                        row[f'{mode}_ppc'] = len(plausible_patches)
                        row[f'{mode}_rc'] = repair_cost
                        row[f'{mode}_fppt'] = first_plausible_patch_try
                        row[f'{mode}_fppcl'] = first_plausible_patch_conv_len
                        row[f'{mode}_mts'] = max_tries

                        for i, plausible_patch in enumerate(plausible_patches):
                            with open(f'{plausible_patches_folder}/{framework_name}/{project}_{bug_id}_{mode}_{i}.txt', 'w+') as f:
                                f.writelines(plausible_patch)

                with open(f'{bug_details_folder}/{framework_name}_{project}_{bug_id}.txt', 'w') as f:
                    vars_object = vars(bug)
                    f.write(json.dumps(vars_object, indent=4, sort_keys=True))
            else:
                print(f"Skipping {project}-{bug_id} because it is not SL, SH or SF bug")
                row['comment'] += "Not SL, SH or SF bug. "

            with open(summary_file_path, 'a', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writerow(row)

if __name__ == "__main__":
    main()