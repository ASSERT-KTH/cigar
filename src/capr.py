from src.chatgpt import ChatGPT
from src.framework import Framework, Bug

class CAPR(object):
    def __init__(self, chatgpt: ChatGPT, framework: Framework,  max_conv_length, max_tries):
        self.chatgpt = chatgpt
        self.framework = framework
        self.max_conversation_length = max_conv_length
        self.max_tries = max_tries

    def repair(self, bug: Bug, sample_per_try=1):
        plausable_patches = []
        current_tries = 0
        total_cost = 0

        while (current_tries < self.max_tries and len(plausable_patches) == 0):
            current_conversation_length = 0
            prompt = self.construct_initial_prompt(bug)

            while (current_conversation_length < self.max_conversation_length and current_tries < self.max_tries):
                patch, cost = self.chatgpt.call(prompt, num_of_samples=sample_per_try, call_id=current_tries)
                total_cost += cost
                
                patch_test_results = self.framework.run_test(patch)
                if patch_test_results == "PASS":
                    plausable_patches.append(patch)
                    break
                elif patch_test_results == bug.test_error_message:
                    feedback = {"role": "user", "content": "The proposed line still does not fix the original test failure. Please provide the correct line in place of INFILL to fix the bug without any comments before or after the code."}
                else:
                    feedback = self.construct_feedback_message(patch_test_results)
                
                prompt.append({"role": "assistant", "content": f"""{patch}"""})
                prompt.append(feedback)
                
                current_tries += 1
                current_conversation_length += 1
        
        if len(plausable_patches) != 0:
            while (current_tries < self.max_tries):
                prompt = self.construct_plausable_path_prompt(bug, plausable_patches)

                patch, cost = self.chatgpt.call(prompt)
                total_cost += cost

                patch_test_results = self.framework.run_test(patch)
                if patch_test_results == "PASS" and patch not in plausable_patches:
                    plausable_patches.append(patch)
                
                current_tries += 1
        
        return plausable_patches, total_cost


    def construct_initial_prompt(self, bug: Bug):
        return [{"role": "system", "content": "You are an automated program repair tool. Only answer with the code that fixes the bug. Avoid comments before and after the code."},
        {"role": "user", "content": f"""Here are some examples of previous bug fixes
{bug.previous_bug_fixes}

The following Java code contains a buggy line that has been replaced with INFILL:
{bug.masked_buggy_code}

This was the original buggy line which was at the INFILL location:
{bug.buggy_line}

The code fails on this test:
{bug.test_name}

on this test line:
{bug.test_line}

with this error message:
{bug.test_error_message}

Please provide the correct line in place of INFILL to fix the bug without any comments before or after the code.        
"""}]
    
    def construct_feedback_message(self, patch_test_results):
        return {"role": "user", "content": f"""The proposed line is incorrect. It has now the following error message:
        {patch_test_results}
        Please provide the correct line in place of INFILL to fix the bug without any comments before or after the code."""}

    def construct_plausable_path_prompt(self, bug: Bug, plausable_patches):
        return [{"role": "system", "content": "You are an automated repair tool. Only answer with the code that fixes the bug. Avoid comments before and after the code."},
        {"role": "user", "content": f"""{bug.previous_bug_fixes}

        The following code contains a buggy line that has been removed:
        {bug.masked_buggy_code}

        The code fails on this test:
        {bug.test_name}

        on this test line:
        {bug.test_line}

        with this error message:
        {bug.test_error_message}
        
        It can be fixed by the following lines:""" + (f"""{i+1}. {patch}
""" for i, patch in range(plausable_patches)) + "Please generate more alternative lines in place of INFILL that fixes the bug."}]
    