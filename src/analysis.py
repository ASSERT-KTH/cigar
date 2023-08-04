import csv
import logging
from pathlib import Path
from src.capr import Capr
from src.rapidcapr import RapidCapr
from src.framework import Framework
from prog_params import ProgParams as prog_params

class Analysis:

    def __init__(self, apr: Capr or RapidCapr, framework: Framework):
        self.apr = apr
        self.framework = framework

        self.plausible_patches_folder = Path(__file__).parent.parent / 'output' / f'{framework.name}_{apr.name}' / 'plausible_patches'

    def run(self, list_of_bugs_to_fix):
        logging.basicConfig(level=prog_params.logging_level, format='%(funcName)s :: %(levelname)s :: %(message)s')

        for project, ids in list_of_bugs_to_fix:

            summary_file_path = Path(__file__).parent.parent / 'output' / f'{self.framework.name}_{self.apr.name}' / f'{project}_summary.csv'

            fieldnames = self._get_fieldnames()
            with open(summary_file_path, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

            for bug_id in ids:
                logging.info(f" ---------- Reproducing {project}-{bug_id} ----------")
                bug = self.framework.get_bug_details(project, bug_id)

                row = {key: "" for key in fieldnames}
                row['framework'] = f"{self.framework.name}"
                row['project'] = project
                row['bug_id'] = bug_id
                row['bug_type'] = bug.bug_type
                if self.apr.name.lower() == "capr":
                    row['max_conv_length'] = prog_params.capr_max_conv_length

                if bug.bug_type != "OT":
                    modes = list(bug.bug_type.split()) if self.apr.name.lower() == "capr" else [bug.bug_type]

                    for mode in modes:
                        logging.info(f" --- Started repairing {project}-{bug_id} ({mode}) --- ")

                        if self.apr.name.lower() == "capr":
                            max_tries = prog_params.capr_SL_SH_max_tries if mode in ['SL', 'SH'] else prog_params.capr_SF_max_tries
                            repair_results = self.apr.repair(bug=bug, 
                                                            mode=mode, 
                                                            n_shot_count=prog_params.capr_n_shot_count,
                                                            max_tries=max_tries,
                                                            max_conv_length=prog_params.capr_max_conv_length)
                        elif self.apr.name.lower() == "rapidcapr":
                            max_tries = prog_params.rapidcapr_max_rounds * 2 * prog_params.rapidcapr_max_fpps_try_per_mode + prog_params.rapidcapr_max_mpps_try_per_mode
                            repair_results = self.apr.repair(bug=bug,
                                                             max_fpps_try_per_mode=prog_params.rapidcapr_max_fpps_try_per_mode,
                                                             max_mpps_try_per_mode=prog_params.rapidcapr_max_mpps_try_per_mode,
                                                             prompt_token_limit=prog_params.rapidcapr_prompt_token_limit,
                                                             total_token_limit_target=prog_params.rapidcapr_total_token_limit_target,
                                                             max_sample_count=prog_params.rapidcapr_max_sample_count,
                                                             similarity_threshold=prog_params.rapidcapr_similarity_threshold,
                                                             max_rounds=prog_params.rapidcapr_max_rounds)
                        plausible_patches, plausible_patch_diffs, repair_cost, first_plausible_patch_try, first_plausible_patch_conv_len, used_tries, err_tf, err_ce, tpc = repair_results

                        prefix = f"{mode}_" if self.apr.name.lower() == "capr" else ""
                        row[f'{prefix}ppc'] = len(plausible_patches)
                        row[f'{prefix}rc'] = repair_cost
                        row[f'{prefix}uts'] = used_tries
                        row[f'{prefix}mts'] = max_tries
                        row[f'{prefix}errtf'] = err_tf
                        row[f'{prefix}errce'] = err_ce
                        row[f'{prefix}tpc'] = tpc
                        if len(plausible_patches) > 0:
                            row[f'{prefix}fppt'] = first_plausible_patch_try
                            if self.apr.name.lower() == "capr":
                                row[f'{prefix}fppcl'] = first_plausible_patch_conv_len
                            logging.info(f"Finished repair attempt of {project}-{bug_id} ({mode}), found {len(plausible_patches)} plausible patches. Used {used_tries} tries totalling {repair_cost} tokens.")
                        else:
                            logging.info(f"Finished repair attempt of {project}-{bug_id} ({mode}), no plausible patches found. Used {used_tries} tries totalling {repair_cost} tokens.")

                        for i, plausible_patch_diff in enumerate(plausible_patch_diffs):
                            with open(f'{self.plausible_patches_folder}/{project}_{bug_id}_{prefix}{i}.diff', 'w+') as f:
                                f.writelines(plausible_patch_diff)

                else:
                    logging.info(f" --- Skipping {project}-{bug_id}, not SL, SH or SF bug. --- ")
                    row['comment'] += "Not SL, SH or SF bug. "

                with open(summary_file_path, 'a', newline='') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writerow(row)

    def _get_fieldnames(self):
        if self.apr.name.lower() == "capr":
            return ['framework', 'project', 'bug_id', 'bug_type',
                    'SL_ppc', 'SL_rc', 'SL_fppt', 'SL_fppcl', 'SL_uts', 'SL_mts', 'SL_errtf', 'SL_errce', 'SL_tpc',
                    'SH_ppc', 'SH_rc', 'SH_fppt', 'SH_fppcl', 'SH_uts', 'SH_mts', 'SH_errtf', 'SH_errce', 'SH_tpc',
                    'SF_ppc', 'SF_rc', 'SF_fppt', 'SF_fppcl', 'SF_uts', 'SF_mts', 'SF_errtf', 'SF_errce', 'SF_tpc',
                    'max_conv_length', 'comment']
        elif self.apr.name.lower() == "rapidcapr": # TODO
            return ['framework', 'project', 'bug_id', 'bug_type',
                    'ppc', 'rc', 'fppt', 'uts', 'mts', 'errtf', 'errce', 'tpc',
                    'comment']
