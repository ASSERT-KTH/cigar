import logging
import openai
from src.chatgpt import ChatGPT
from src.framework import Framework
from src.bug import Bug
from src.prompts import Prompts as prompts
from prog_params import ProgParams as prog_params

class RapidCapr(object):

    def __init__(self, chatgpt: ChatGPT, framework: Framework):
        self.chatgpt = chatgpt
        self.framework = framework
    
    def repair(self, bug: Bug, max_fpps_try_per_mode=1, max_mpps_try_per_mode=1):

        plausible_patches, plausible_patch_diffs = [], []
        first_plausible_patch_try, current_conversation_length = 0, 0
        current_tries, total_cost = 0, 0
        err_tf, err_ce = 0, 0
        prefix = f"{self.framework.test_framework}_{bug.project}_{bug.bug_id}"

        modes = ["SL", "SF"] if "SL" in bug.bug_type else list(bug.bug_type.split())
        for mode in modes:

            n_shot_bugs=self.framework.get_n_shot_bugs(n=1, bug=bug, mode=mode)
            current_fpps_try_in_mode = 0
            proposed_patches = []

            while (current_fpps_try_in_mode < max_fpps_try_per_mode and len(plausible_patches) == 0):
                
                prompt = self.construct_fpps_prompt(bug=bug, mode=mode, proposed_patches=proposed_patches, n_shot_bugs=n_shot_bugs)
                num_of_samples = 5 # TODO determine later

                current_tries += 1
                current_fpps_try_in_mode += 1

                logging.info(f"Searching for plausible patch in {bug.project}-{bug.bug_id} ({mode}), try {current_tries} (ccl: {current_conversation_length})")
                try:
                    responses, cost = self.chatgpt.call(prompt, num_of_samples=num_of_samples, prefix=f"{prefix}_{current_tries}")
                except openai.error.InvalidRequestError as e:
                    logging.info(e)
                    err_ce += 1 # Count token exceeded limit as error
                    total_cost += prog_params.gpt35_model_token_limit # Exceeded Token limit
                    continue

                total_cost += cost

                for response in responses:
                    patches = self.extract_patches_from_response(response)
                    for patch, patch_mode in patches:
                        logging.debug(f"Validating response of {bug.project}-{bug.bug_id} ({mode})")
                        test_result, result_reason, patch_diff = self.framework.validate_patch(bug=bug, proposed_patch=patch, mode=patch_mode)

                        if patch not in [p["patch"] for p in proposed_patches]:
                            proposed_patches.append({"patch": patch, "test_result": test_result, "result_reason": result_reason})

                        if test_result == "PASS" and patch not in plausible_patches:
                            plausible_patches.append(patch)
                            plausible_patch_diffs.append(patch_diff)

                            if first_plausible_patch_try == 0:
                                first_plausible_patch_try = current_tries
                            logging.debug(f"Proposed patch of {bug.project}-{bug.bug_id} ({mode}) patch passed all tests")
                        else:
                            if test_result == "FAIL":
                                err_tf += 1
                            elif test_result == "ERROR":
                                err_ce += 1

            if len(plausible_patches) != 0:
                current_mpps_try_in_mode = 0

                while (current_mpps_try_in_mode < max_mpps_try_per_mode):          
                    current_tries += 1
                    current_mpps_try_in_mode += 1

                    logging.info(f"Attempt to generate multiple plausible patches in {bug.project}-{bug.bug_id} ({mode}), try {current_tries} (pps: {len(plausible_patches)})")
                    prompt = self.construct_mpps_prompt(bug=bug, mode=mode, plausible_patches=plausible_patches, n_shot_bugs=n_shot_bugs)
                    num_of_samples = 5 # TODO determine later

                    try:
                        responses, cost = self.chatgpt.call(prompt, num_of_samples=num_of_samples, prefix=f"{prefix}_{current_tries}")
                    except openai.error.InvalidRequestError as e:
                        logging.info(e)
                        err_ce += 1 # Count token exceeded limit as error
                        total_cost += prog_params.gpt35_model_token_limit # Exceeded Token limit
                        break

                    total_cost += cost

                    for response in responses:
                        patches = self.extract_patches_from_response(response)
                        for patch, patch_mode in patches:
                            logging.debug(f"Validating response of {bug.project}-{bug.bug_id} ({mode})")
                            test_result, result_reason, patch_diff = self.framework.validate_patch(bug=bug, proposed_patch=patch, mode=patch_mode)

                            if test_result == "PASS" and patch not in plausible_patches:
                                plausible_patches.append(patch)
                                plausible_patch_diffs.append(patch_diff)

                            if test_result == "FAIL":
                                err_tf += 1
                            elif test_result == "ERROR":
                                err_ce += 1
                                
                break
        
        return plausible_patches, plausible_patch_diffs, total_cost, first_plausible_patch_try, current_conversation_length, current_tries, err_tf, err_ce
    
    def extract_patches_from_response(self, response):

        if "```java" in response:
            patch = response[response.find("```java")+len("```java")+1:]
            patch = patch[:patch.find("\n```")]
        else:
            patch = response

        patch_mode = None
        return patch, patch_mode
    
    def construct_fpps_prompt(self, bug, mode, proposed_patches, n_shot_bugs):
        prompt = prompts.construct_initial_prompt(bug=bug, mode=mode, n_shot_bugs=n_shot_bugs)
        return prompt
    
    def construct_mpps_prompt(self, bug, mode, plausible_patches):
        prompt = prompts.construct_plausible_path_prompt(bug, plausible_patches, mode)
        return prompt