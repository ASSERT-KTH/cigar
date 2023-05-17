from src.chatgpt import ChatGPT
from src.framework import Framework
from src.bug import Bug
from src.prompts import Prompts as prompts

class CAPR(object):
    def __init__(self, chatgpt: ChatGPT, framework: Framework,  max_conv_length, max_tries):
        self.chatgpt = chatgpt
        self.framework = framework
        self.max_conversation_length = max_conv_length
        self.max_tries = max_tries

    def repair(self, bug: Bug, mode: str, n_shot_count=1, sample_per_try=1, stop_after_first_plausible_patch=False):
        assert mode in ["SL", "SH", "SF"]
        plausable_patches = []
        first_plausible_patch_try = 0
        current_conversation_length = 0
        current_tries = 1
        total_cost = 1
        prefix = f"{self.framework.test_framework}_{bug.project}_{bug.bug_id}_{mode}"

        while (current_tries < self.max_tries and len(plausable_patches) == 0):
            current_conversation_length = 1
            n_shot_bugs=self.framework.get_n_shot_bugs(n=n_shot_count, bug=bug, mode=mode)
            prompt = prompts.construct_initial_prompt(bug=bug, mode=mode, n_shot_bugs=n_shot_bugs)

            while (current_conversation_length <= self.max_conversation_length and current_tries <= self.max_tries):
                response, cost = self.chatgpt.call(prompt, num_of_samples=sample_per_try, prefix=f"{prefix}_{current_tries}")
                total_cost += cost

                patch = self.extract_patch_from_response(response)
                
                test_result, result_reason = self.framework.validate_patch(bug=bug, proposed_patch=patch, mode=mode)
                if test_result == "PASS":
                    plausable_patches.append(patch)
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
        
        if len(plausable_patches) != 0 and not stop_after_first_plausible_patch:
            while (current_tries <= self.max_tries):
                prompt = prompts.construct_plausable_path_prompt(bug, plausable_patches, mode)

                response, cost = self.chatgpt.call(prompt, num_of_samples=sample_per_try, prefix=f"{prefix}_{current_tries}")
                total_cost += cost

                patch = self.extract_patch_from_response(response)

                test_result, result_reason = self.framework.validate_patch(bug, patch)
                if test_result == "PASS" and patch not in plausable_patches:
                    plausable_patches.append(patch)
                
                current_tries += 1
        
        return plausable_patches, total_cost, first_plausible_patch_try, current_conversation_length
    
    def extract_patch_from_response(self, response):

        if "```java" in response:
            patch = response[response.find("```java")+len("```java")+1:]
            patch = patch[:patch.find("\n```")]
        else:
            patch = response

        return patch
    