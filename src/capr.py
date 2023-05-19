from src.chatgpt import ChatGPT
from src.framework import Framework
from src.bug import Bug
from src.prompts import Prompts as prompts

class CAPR(object):
    def __init__(self, chatgpt: ChatGPT, framework: Framework):
        self.chatgpt = chatgpt
        self.framework = framework

    def repair(self, bug: Bug, mode: str, n_shot_count=1, sample_per_try=1, max_conv_length=3, max_tries=1, stop_after_first_plausible_patch=False):
        assert mode in ["SL", "SH", "SF"]
        n_shot_bugs=self.framework.get_n_shot_bugs(n=n_shot_count, bug=bug, mode=mode)

        plausible_patches = []
        plausible_patch_diffs = []
        first_plausible_patch_try = 0
        current_conversation_length = 0
        current_tries = 1
        total_cost = 1
        prefix = f"{self.framework.test_framework}_{bug.project}_{bug.bug_id}_{mode}"

        while (current_tries <= max_tries and len(plausible_patches) == 0):
            current_conversation_length = 0
            prompt = prompts.construct_initial_prompt(bug=bug, mode=mode, n_shot_bugs=n_shot_bugs)

            while (current_conversation_length < max_conv_length and current_tries <= max_tries):
                response, cost = self.chatgpt.call(prompt, num_of_samples=sample_per_try, prefix=f"{prefix}_{current_tries}")
                total_cost += cost

                patch = self.extract_patch_from_response(response)
                test_result, result_reason, patch_diff = self.framework.validate_patch(bug=bug, proposed_patch=patch, mode=mode)

                if test_result == "PASS":
                    plausible_patches.append(patch)
                    plausible_patch_diffs.append(patch_diff)
                    first_plausible_patch_try = current_tries
                    current_tries += 1
                    break
                elif result_reason == bug.test_error_message:
                    feedback = prompts.test_fail_feedback()
                else:
                    feedback = prompts.construct_feedback_prompt(test_result, result_reason, mode)
                
                prompt.append({"role": "assistant", "content": f"""{response}"""})
                prompt.append(feedback)
                
                current_tries += 1
                current_conversation_length += 1
        
        if len(plausible_patches) != 0 and not stop_after_first_plausible_patch:
            while (current_tries <= max_tries):
                prompt = prompts.construct_plausable_path_prompt(bug, plausible_patches, mode)

                response, cost = self.chatgpt.call(prompt, num_of_samples=sample_per_try, prefix=f"{prefix}_{current_tries}")
                total_cost += cost

                patch = self.extract_patch_from_response(response)

                test_result, result_reason, patch_diff = self.framework.validate_patch(bug, patch)
                if test_result == "PASS" and patch not in plausible_patches:
                    plausible_patches.append(patch)
                    plausible_patch_diffs.append(patch_diff)
                
                current_tries += 1
        
        return plausible_patches, plausible_patch_diffs, total_cost, first_plausible_patch_try, current_conversation_length
    
    def extract_patch_from_response(self, response):

        if "```java" in response:
            patch = response[response.find("```java")+len("```java")+1:]
            patch = patch[:patch.find("\n```")]
        else:
            patch = response

        return patch
    