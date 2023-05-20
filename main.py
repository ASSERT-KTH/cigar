import csv
import json
import logging
from pathlib import Path
from src.capr import CAPR
from src.chatgpt import ChatGPT
from src.framework import Framework
from prog_params import ProgParams as prog_params
from user_params import UserParams as user_params

def main():
    logging.basicConfig(level=user_params.logging_level, format='%(funcName)s :: %(levelname)s :: %(message)s')

    framework = Framework(test_framework="defects4j",
                          list_of_bugs = prog_params.list_of_d4j_bugs, 
                          d4j_path=user_params.D4J_PATH,
                          tmp_dir=user_params.TMP_DIR,
                          validate_patch_cache_folder=prog_params.validate_patch_cache_folder,
                          n_shot_cache_folder=prog_params.n_shot_cache_folder,
                          bug_details_cache_folder=prog_params.bug_details_cache_folder)
    chatgpt = ChatGPT(model=prog_params.model, 
                      api_key=user_params.API_KEY,
                      cache_folder=prog_params.chatgpt_cache_folder,
                      load_from_cache=True,
                      save_to_cache=True)
    capr = CAPR(chatgpt=chatgpt, 
                framework=framework)
    
    summary_file_path = Path(__file__).parent / 'data' / 'output' / 'summary.csv'
    plausible_patches_folder = Path(__file__).parent / 'data' / 'output' / 'plausible_patches'

    fieldnames = ['framework', 'project', 'bug_id', 'bug_type',
                  'SL_ppc', 'SL_rc', 'SL_fppt', 'SL_fppcl', 'SL_mts',
                  'SH_ppc', 'SH_rc', 'SH_fppt', 'SH_fppcl', 'SH_mts',
                  'SF_ppc', 'SF_rc', 'SF_fppt', 'SF_fppcl', 'SF_mts',
                  'max_conv_length', 'comment']
    with open(summary_file_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

    for project, ids in user_params.list_of_bugs_to_fix:
        for bug_id in ids:
            logging.info(f" ---------- Reproducing {project}-{bug_id} ----------")
            bug = framework.get_bug_details(project, bug_id)

            row = {key: "" for key in fieldnames}
            row['framework'] = "defects4j"
            row['project'] = project
            row['bug_id'] = bug_id
            row['bug_type'] = bug.bug_type
            row['max_conv_length'] = user_params.max_conv_length

            if bug.bug_type != "OT":
                for mode in ['SL', 'SH', 'SF']:
                    if mode in bug.bug_type:
                        max_tries = user_params.SL_SH_max_tries if mode in ['SL', 'SH'] else user_params.SF_max_tries
                        logging.info(f" --- Started repairing {project}-{bug_id} ({mode}) --- ")
                        repair_results = capr.repair(bug=bug, 
                                                     mode=mode, 
                                                     n_shot_count=user_params.n_shot_count,
                                                     stop_after_first_plausible_patch=True,
                                                     max_tries=max_tries,
                                                     max_conv_length=user_params.max_conv_length)
                        plausible_patches, plausible_patch_diffs, repair_cost, first_plausible_patch_try, first_plausible_patch_conv_len = repair_results
                        logging.debug(f"Finished repair of {project}-{bug_id} ({mode})")

                        row[f'{mode}_ppc'] = len(plausible_patches)
                        row[f'{mode}_rc'] = repair_cost
                        row[f'{mode}_mts'] = max_tries
                        if len(plausible_patches) > 0:
                            row[f'{mode}_fppt'] = first_plausible_patch_try
                            row[f'{mode}_fppcl'] = first_plausible_patch_conv_len

                        for i, plausible_patch_diff in enumerate(plausible_patch_diffs):
                            with open(f'{plausible_patches_folder}/{project}_{bug_id}_{mode}_{i}.diff', 'w+') as f:
                                f.writelines(plausible_patch_diff)

            else:
                logging.info(f" --- Skipping {project}-{bug_id}, not SL, SH or SF bug. --- ")
                row['comment'] += "Not SL, SH or SF bug. "

            with open(summary_file_path, 'a', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writerow(row)

if __name__ == "__main__": 
    main()