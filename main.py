import csv
import json
import logging
from pathlib import Path
from src.capr import CAPR
from src.chatgpt import ChatGPT
from src.framework import Framework
from prog_params import ProgParams as prog_params
from user_params import UserParams as user_params

def main(project=None, bug_ids=None):
    logging.basicConfig(level=prog_params.logging_level, format='%(funcName)s :: %(levelname)s :: %(message)s')

    framework = Framework(test_framework="defects4j", list_of_bugs = prog_params.d4j_list_of_bugs, 
                          d4j_path=user_params.D4J_PATH, java_home=user_params.JAVA_HOME, tmp_dir=user_params.TMP_DIR,
                          validate_patch_cache_folder=prog_params.validate_patch_cache_folder,
                          n_shot_cache_folder=prog_params.n_shot_cache_folder,
                          bug_details_cache_folder=prog_params.bug_details_cache_folder)
    chatgpt = ChatGPT(model=prog_params.gpt35_model, api_key=user_params.API_KEY,
                      cache_folder=prog_params.gpt35_cache_folder,
                      load_from_cache=True, save_to_cache=True)
    capr = CAPR(chatgpt=chatgpt, 
                framework=framework)
    
    plausible_patches_folder = Path(__file__).parent / 'output' / 'plausible_patches'

    if project is not None and bug_ids is not None:
        list_of_bugs_to_fix = [(project, bug_ids)]
    elif project is not None:
        list_of_bugs_to_fix = [(project, [ids for proj, ids in prog_params.d4j_list_of_bugs if proj == project][0])]
    else:
        list_of_bugs_to_fix = prog_params.d4j_list_of_bugs

    for project, ids in list_of_bugs_to_fix:

        summary_file_path = Path(__file__).parent / 'output' / f'{project}_summary.csv'

        fieldnames = ['framework', 'project', 'bug_id', 'bug_type',
                    'SL_ppc', 'SL_rc', 'SL_fppt', 'SL_fppcl', 'SL_uts', 'SL_mts', 'SL_errtf', 'SL_errce',
                    'SH_ppc', 'SH_rc', 'SH_fppt', 'SH_fppcl', 'SH_uts', 'SH_mts', 'SH_errtf', 'SH_errce',
                    'SF_ppc', 'SF_rc', 'SF_fppt', 'SF_fppcl', 'SF_uts', 'SF_mts', 'SF_errtf', 'SF_errce',
                    'max_conv_length', 'comment']
        if bug_ids is None:
            with open(summary_file_path, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

        for bug_id in ids:
            logging.info(f" ---------- Reproducing {project}-{bug_id} ----------")
            bug = framework.get_bug_details(project, bug_id)

            row = {key: "" for key in fieldnames}
            row['framework'] = "defects4j"
            row['project'] = project
            row['bug_id'] = bug_id
            row['bug_type'] = bug.bug_type
            row['max_conv_length'] = prog_params.capr_max_conv_length

            if bug.bug_type != "OT":
                for mode in ['SL', 'SH', 'SF']:
                    if mode in bug.bug_type:
                        max_tries = prog_params.capr_SL_SH_max_tries if mode in ['SL', 'SH'] else prog_params.capr_SF_max_tries
                        logging.info(f" --- Started repairing {project}-{bug_id} ({mode}) --- ")
                        repair_results = capr.repair(bug=bug, 
                                                     mode=mode, 
                                                     n_shot_count=prog_params.capr_n_shot_count,
                                                     max_tries=max_tries,
                                                     max_conv_length=prog_params.capr_max_conv_length)
                        plausible_patches, plausible_patch_diffs, repair_cost, first_plausible_patch_try, first_plausible_patch_conv_len, used_tries, err_tf, err_ce = repair_results

                        row[f'{mode}_ppc'] = len(plausible_patches)
                        row[f'{mode}_rc'] = repair_cost
                        row[f'{mode}_uts'] = used_tries
                        row[f'{mode}_mts'] = max_tries
                        row[f'{mode}_errtf'] = err_tf
                        row[f'{mode}_errce'] = err_ce
                        if len(plausible_patches) > 0:
                            row[f'{mode}_fppt'] = first_plausible_patch_try
                            row[f'{mode}_fppcl'] = first_plausible_patch_conv_len
                            logging.info(f"Finished repair attempt of {project}-{bug_id} ({mode}), found {len(plausible_patches)} plausible patches. Used {used_tries} tries totalling {repair_cost} tokens.")
                        else:
                            logging.info(f"Finished repair attempt of {project}-{bug_id} ({mode}), no plausible patches found. Used {used_tries} tries totalling {repair_cost} tokens.")

                        for i, plausible_patch_diff in enumerate(plausible_patch_diffs):
                            with open(f'{plausible_patches_folder}/{project}_{bug_id}_{mode}_{i}.diff', 'w+') as f:
                                f.writelines(plausible_patch_diff)

            else:
                logging.info(f" --- Skipping {project}-{bug_id}, not SL, SH or SF bug. --- ")
                row['comment'] += "Not SL, SH or SF bug. "

            if bug_ids is None:
                with open(summary_file_path, 'a', newline='') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writerow(row)

if __name__ == '__main__':
    import argparse

    project_choices = [p for p, _ in prog_params.d4j_list_of_bugs]

    parser = argparse.ArgumentParser(description='Run CAPR on D4J Bugs')

    parser.add_argument('-p', '--proj', metavar='path', required=False, help='Project name', 
                        choices=project_choices)
    parser.add_argument('-bs', '--bug_ids', metavar='path', required=False, help='List of bug_ids to repair', type=int, nargs='+')
    
    args = parser.parse_args()
    main(project=args.proj, bug_ids=args.bug_ids)
