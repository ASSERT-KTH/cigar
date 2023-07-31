import openai
from prog_params import ProgParams as prog_params
from src.chatgpt import ChatGPT
from src.framework import Framework
from src.bug import Bug
from src.prompts import Prompts as prompts
from src.proposed_patches import ProposedPatches
from src.utils import extract_patches_from_response

class RapidCapr(object):

    def __init__(self, chatgpt: ChatGPT, framework: Framework):
        self.chatgpt = chatgpt
        self.framework = framework
    
    def repair(self, bug: Bug, max_fpps_try_per_mode=1, max_mpps_try_per_mode=1, prompt_token_limit=1500, total_token_limit_target=3000, 
               max_sample_count=50, similarity_threshold=0.5, ask_for_bug_description=False):

        modes = ["SL", "SF"] if "SL" in bug.bug_type else list(bug.bug_type.split())
        prefix = f"{self.framework.test_framework}_{bug.project}_{bug.bug_id}"
        total_call_tries, total_cost = 0, 0
        
        proposed_patches = ProposedPatches()

        for mode in modes:

            n_shot_bugs=self.framework.get_n_shot_bugs(n=1, bug=bug, mode=mode)
            
            for run_condition, call_try_limit, construct_prompt_function in [(False, max_fpps_try_per_mode, prompts.construct_fpps_prompt), 
                                                                             (True, max_mpps_try_per_mode, prompts.construct_mpps_prompt)]:
                call_tries = 0

                while(call_tries < call_try_limit and proposed_patches.contains_plausible_patch(mode) == run_condition):
                    total_call_tries += 1
                    call_tries += 1

                    prompt, num_of_samples = construct_prompt_function(bug=bug, mode=mode, proposed_patches=proposed_patches, n_shot_bugs=n_shot_bugs,
                                                                       prompt_token_limit=prompt_token_limit, total_token_limit_target=total_token_limit_target,
                                                                       ask_for_bug_description=ask_for_bug_description)
                    try:
                        responses, cost = self.chatgpt.call(prompt, num_of_samples=min(max_sample_count,num_of_samples), prefix=f"{prefix}_{total_call_tries}")
                        total_cost += cost
                    except openai.error.InvalidRequestError as e:
                        total_cost += prog_params.gpt35_model_token_limit # Exceeded Token limit
                        continue

                    for response in responses:
                        patches = extract_patches_from_response(bug=bug, response=response, response_mode=mode, similarity_threshold=similarity_threshold)
                        for patch, patch_mode in patches:
                            test_result, result_reason, patch_diff = self.framework.validate_patch(bug=bug, proposed_patch=patch, mode=patch_mode)
                            proposed_patches.add(response=response, test_result=test_result, result_reason=result_reason, mode=patch_mode, 
                                                 patch=patch, patch_diff=patch_diff)
        
            if proposed_patches.contains_plausible_patch(mode=mode) == True:
                break
        
        return (proposed_patches.get_plausible_patches(), proposed_patches.get_plausible_patch_diffs(), 
                total_cost, proposed_patches.get_call_num_of_first_plausible_patch(), None, total_call_tries, 
                proposed_patches.get_test_failure_count(), proposed_patches.get_test_error_count())
