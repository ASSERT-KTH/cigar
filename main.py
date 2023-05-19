import csv
import json
from pathlib import Path
from src.capr import CAPR
from src.chatgpt import ChatGPT
from src.framework import Framework

def main():
    SL_SH_max_tries, SF_max_tries = 6, 6
    n_shot_count = 1
    max_conv_length = 3
    framework_name = "defects4j"
    list_of_bugs_to_fix = [ # All Bugs fixed by the authors
        # ("Chart", [1, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 17, 20, 24, 26]),
        # ("Closure", [2, 5, 7, 10, 11, 13, 15, 18, 19, 20, 22, 31, 33, 36, 38, 44, 51, 52, 56, 57, 58, 61, 62, 65, 67, 70, 73, 77, 78, 83, 86, 92, 94, 97, 101, 102, 104, 107, 119, 122, 124, 125, 126, 128, 129, 131, ]),
        # ("Lang", [3, 10, 11, 12, 14, 16, 18, 21, 22, 24, 26, 27, 28, 29, 31, 33, 37, 38, 39, 40, 42, 43, 44, 45, 48, 51, 52, 54, 55, 57, 58, 59, 61]),
        # ("Math", [2, 3, 5, 8, 10, 11, 17, 19, 20, 23, 24, 25, 26, 27, 28, 30, 32, 33, 34, 39, 41, 42, 45, 48, 50, 53, 56, 57, 58, 59, 60, 63, 69, 70, 72, 73, 75, 78, 79, 80, 82, 85, 86, 87, 88, 89, 91, 94, 95, 96, 97, 101, 105, 106]),
        # ("Mockito", [12, 22, 24, 29, 33, 34, 38]),
        # ("Time", [4, 5, 15, 16, 18, 19, 20])
        ("Time", [19])
    ]
    tmp_dir = f"/tmp/{framework_name}"
    d4j_path = "/Users/davidhidvegi/Desktop/defects4j/framework/bin"

    framework = Framework(test_framework=framework_name,
                          list_of_bugs = [("Chart", [i for i in range(1, 27)]),
                                          ("Closure", [i for i in range(1, 177) if i != 63 and i != 93]),
                                          ("Lang", [i for i in range(1, 66) if i != 2]),
                                          ("Math", [i for i in range(1, 107)]),
                                          ("Mockito", [i for i in range(1, 39)]), # Failed to reproduce bugs on macOS and Ubuntu
                                          ("Time", [i for i in range(1, 28) if i != 21])], 
                          d4j_path=d4j_path,
                          tmp_dir=tmp_dir,
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

    fieldnames = ['framework', 'project', 'bug_id', 'bug_type',
                  'SL_ppc', 'SL_rc', 'SL_fppt', 'SL_fppcl', 'SL_mts',
                  'SH_ppc', 'SH_rc', 'SH_fppt', 'SH_fppcl', 'SH_mts',
                  'SF_ppc', 'SF_rc', 'SF_fppt', 'SF_fppcl', 'SF_mts',
                  'max_conv_length', 'comment']
    with open(summary_file_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

    for project, ids in list_of_bugs_to_fix:
        for bug_id in ids:
            print(f"\n\nReproducing {project}-{bug_id}")
            bug = framework.reproduce_bug(project, bug_id)

            row = {key: "" for key in fieldnames}
            row['framework'] = framework_name
            row['project'] = project
            row['bug_id'] = bug_id
            row['bug_type'] = bug.bug_type
            row['max_conv_length'] = max_conv_length

            if bug.bug_type != "OT":
                for mode in ['SL', 'SH', 'SF']:
                    if mode in bug.bug_type:
                        max_tries = SL_SH_max_tries if mode in ['SL', 'SH'] else SF_max_tries
                        print(f"\nStarted repairing {project}-{bug_id} ({mode})")
                        plausible_patches, plausible_patch_diffs, repair_cost, first_plausible_patch_try, first_plausible_patch_conv_len = capr.repair(bug=bug, 
                                                                                                                                                       mode=mode, 
                                                                                                                                                       n_shot_count=n_shot_count,
                                                                                                                                                       stop_after_first_plausible_patch=True,
                                                                                                                                                       max_tries=max_tries,
                                                                                                                                                       max_conv_length=max_conv_length)
                        print(f"Finished repair of {project}-{bug_id} ({mode})")

                        row[f'{mode}_ppc'] = len(plausible_patches)
                        row[f'{mode}_rc'] = repair_cost
                        row[f'{mode}_mts'] = max_tries
                        if len(plausible_patches) > 0:
                            row[f'{mode}_fppt'] = first_plausible_patch_try
                            row[f'{mode}_fppcl'] = first_plausible_patch_conv_len

                        for i, plausible_patch_diff in enumerate(plausible_patch_diffs):
                            with open(f'{plausible_patches_folder}/{framework_name}/{project}_{bug_id}_{mode}_{i}.diff', 'w+') as f:
                                f.writelines(plausible_patch_diff)

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