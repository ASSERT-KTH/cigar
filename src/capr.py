from src.chatgpt import ChatGPT
from src.framework import Framework
from src.bug import Bug

class CAPR(object):
    def __init__(self, chatgpt: ChatGPT, framework: Framework,  max_conv_length, max_tries):
        self.chatgpt = chatgpt
        self.framework = framework
        self.max_conversation_length = max_conv_length
        self.max_tries = max_tries

    def repair(self, bug: Bug, sample_per_try=1):
        plausable_patches = []
        first_plausible_patch_try = -1
        current_tries = 0
        total_cost = 0
        prefix = f"{self.framework.test_framework}_{bug.project}_{bug.bug_id}"

        while (current_tries < self.max_tries and len(plausable_patches) == 0):
            current_conversation_length = 0
            prompt = self.construct_initial_prompt(bug)

            while (current_conversation_length < self.max_conversation_length and current_tries < self.max_tries):
                response, cost = self.chatgpt.call(prompt, num_of_samples=sample_per_try, prefix=f"{prefix}_{current_tries}")
                total_cost += cost

                patch = self.extract_patch_from_response(response)
                
                test_result, result_reason = self.framework.validate_patch(bug, patch)
                if test_result == "PASS":
                    plausable_patches.append(patch)
                    first_plausible_patch_try = current_tries
                    current_tries += 1
                    break
                elif result_reason == bug.test_error_message:
                    feedback = {"role": "user", "content": "The fixed version is still not correct.\nPlease fix the correct line at the infill location."}
                else:
                    feedback = self.construct_feedback_message(test_result, result_reason)
                
                prompt.append({"role": "assistant", "content": f"""{response}"""})
                prompt.append(feedback)
                
                current_tries += 1
                current_conversation_length += 1
        
        if len(plausable_patches) != 0:
            while (current_tries < self.max_tries):
                prompt = self.construct_plausable_path_prompt(bug, plausable_patches)

                response, cost = self.chatgpt.call(prompt, num_of_samples=sample_per_try, prefix=f"{prefix}_{current_tries}")
                total_cost += cost

                patch = self.extract_patch_from_response(response)

                test_result, result_reason = self.framework.validate_patch(bug, patch)
                if test_result == "PASS" and patch not in plausable_patches:
                    plausable_patches.append(patch)
                
                current_tries += 1
        
        return first_plausible_patch_try, plausable_patches, total_cost
    
    def extract_patch_from_response(self, response):

        if "```java" in response:
            patch = response[response.find("```java")+len("```java")+1:]
            patch = patch[:patch.find("```")]
            if "\n" in patch:
                patch = patch.split("\n")[0]
        elif "\n\n" in response:
            patch = response.split("\n\n")[1].split("\n")[0]
        else:
            patch = response

        return patch

    def construct_initial_prompt(self, bug: Bug):
        return [{"role": "system", "content": "You are an automated program repair tool. Please answer with the correct line in a code block."},
        {"role": "user", "content": f"""The following Java code contains a buggy line that has been replaced with INFILL:
```java
{bug.masked_buggy_code}
```

This was the original buggy line which was at the INFILL location:
```java
{bug.buggy_line}
```

The code fails on this test:
```java
{bug.test_name}
```

on this test line:
```java
{bug.test_line}
```

with this error message:
```java
{bug.test_error_message}
```

Please provide the correct line at the INFILL location.
"""}]
    
    def construct_feedback_message(self, test_result, result_reason):
        error_type = "test error" if test_result == "FAIL" else "compilation error"
        return {"role": "user", "content": f"""The fixed version is still incorrect, it contains the {error_type}:
{result_reason}
Please provide the correct patch line at the infill location."""}

    def construct_plausable_path_prompt(self, bug: Bug, plausable_patches):
        plausable_patches_text = ""
        for i, patch in enumerate(plausable_patches):
            plausable_patches_text += f"""{i+1}. ```java
{patch}
```
"""

        return [{"role": "system", "content": "You are an automated program repair tool. Please answer with the correct line in a code block."},
        {"role": "user", "content": f"""The following Java code contains a buggy line that has been replaced with INFILL:
```java
{bug.masked_buggy_code}
```

This was the original buggy line which was at the INFILL location:
```java
{bug.buggy_line}
```

The code fails on this test:
```java
{bug.test_name}
```

on this test line:
```java
{bug.test_line}
```

with this error message:
```java
{bug.test_error_message}
```
        
It can be fixed by the following lines:
{plausable_patches_text}

Please generate an alternative fix line."""}]
    