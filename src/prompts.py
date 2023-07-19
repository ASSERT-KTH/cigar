from src.bug import Bug
from src.proposed_patches import ProposedPatches, ProposedPatch
from src.utils import count_num_of_samples, get_token_count

class Prompts(object):

    # CAPR Prompts

    def construct_initial_message(bug: Bug, mode: str, n_shot_bugs=None):
        n_shot_examples_text = ""
        if n_shot_bugs:
            for n_shot_bug in n_shot_bugs:
                n_shot_initial_prompt = Prompts.construct_initial_message(bug=n_shot_bug, mode=mode, n_shot_bugs=None)
                if mode == "SL":
                    n_shot_examples_text += f"{n_shot_initial_prompt}\n\nIt can be fixed by these possible line:\n```java\n{n_shot_bug.fixed_lines}\n```\n\n"
                elif mode == "SH":
                    n_shot_examples_text += f"{n_shot_initial_prompt}\n\nIt can be fixed by the following hunk:\n```java\n{n_shot_bug.fixed_lines}\n```\n\n"
                elif mode == "SF":
                    n_shot_examples_text += f"{n_shot_initial_prompt}\n\nIt can be fixed by the following function:\n```java\n{n_shot_bug.fixed_code}\n```\n\n"

        if mode == "SL":
            prompt_header = f"""The following code contains a buggy line that has been removed.\n```java\n{bug.masked_code}\n```
This was the original buggy line which was removed by the infill location:
```java\n{bug.buggy_lines}\n```"""
            prompt_footer = "Please provide the correct line at the infill location."

        elif mode == "SH":
            prompt_header = f"""The following code contains a buggy hunk that has been removed.\n```java\n{bug.masked_code}\n```
This was the original buggy hunk which was removed by the infill location:
```java\n{bug.buggy_lines}\n```"""
            prompt_footer = "Please provide the correct hunk at the infill location."

        elif mode == "SF":
            prompt_header = f"""The following code contains a bug\n```java\n{bug.code}\n```"""
            prompt_footer = "Please provide the correct function."

        initial_prompt_message= f"""{n_shot_examples_text}{prompt_header}
The code fails on this test:\n```\n{bug.test_name}\n```
on this test line:\n```java\n{bug.test_line}\n```
with the following test error:\n```\n{bug.test_error_message}\n```
{prompt_footer}"""

        return initial_prompt_message

    def construct_initial_prompt(bug: Bug, mode: str, n_shot_bugs=None):

        initial_prompt_message = Prompts.construct_initial_message(bug=bug, mode=mode, n_shot_bugs=n_shot_bugs)

        return [{"role": "system", "content": "You are an automated program repair tool."},
                {"role": "user", "content": initial_prompt_message}]

    def construct_feedback_prompt(test_result, result_reason, mode: str):
        error_type = "test error" if test_result == "FAIL" else "compilation error"
        if mode == "SL":
            call_to_action = "Please provide the correct line at the infill location."
        elif mode == "SH":
            call_to_action = "Please provide the correct hunk at the infill location."
        elif mode == "SF":
            call_to_action = "Please provide the correct function."
        return {"role": "user", "content": f"""The fixed version is still not correct. code has the following {error_type}:\n```\n{result_reason}\n```\n{call_to_action}"""}
    
    def test_fail_feedback():
        return {"role": "user", "content": f"The fixed version is still not correct. It still does not fix the original test failure."}

    def construct_plausible_path_prompt(bug: Bug, plausible_patches, mode: str):

        initial_prompt_message = Prompts.construct_initial_message(bug, mode, n_shot_bugs=None)

        plausible_patches_list_text = ""
        for i, patch in enumerate(plausible_patches):
            plausible_patches_list_text += f"""{i+1}. ```java\n{patch}\n```\n"""

        s = "s" if len(plausible_patches) > 1 else ""

        if mode == "SL":
            more_plausible_patches_text = f"It can be fixed by these possible line{s}:\n{plausible_patches_list_text}Please generate an alternative fix line."
        elif mode == "SH":
            more_plausible_patches_text = f"It can be fixed by the following hunk{s}:\n{plausible_patches_list_text}Please generate an alternative fix hunk."
        elif mode == "SF":
            more_plausible_patches_text = f"It can be fixed by the following function{s}:\n{plausible_patches_list_text}Please generate an alternative fix function."

        return [{"role": "system", "content": "You are an automated program repair tool."},
                {"role": "user", "content": f"{initial_prompt_message}\n{more_plausible_patches_text}"}]
    
    # RapidCapr Messages

    def system_message():
        return "You are an automated program repair tool."
    
    def n_shot_example_message(bug: Bug, n_shot_bugs, mode):

        n_shot_bug = n_shot_bugs[0]
        
        if mode == "SL":
            solution_message += f"It can be fixed by these possible line:\n```java\n{n_shot_bug.fixed_lines}\n```"
        elif mode == "SH":
            solution_message += f"It can be fixed by the following hunk:\n```java\n{n_shot_bug.fixed_lines}\n```"
        elif mode == "SF":
            solution_message += f"It can be fixed by the following function:\n```java\n{n_shot_bug.fixed_code}\n```"
        
        return [Prompts.code_introduction_message(bug=n_shot_bug, mode=mode),
                Prompts.bug_details(bug=n_shot_bug, mode=mode),
                Prompts.fpps_call_to_action(mode=mode),
                solution_message]

    def code_introduction_message(bug: Bug, mode):
        if mode == "SL":
            return f"The following code contains a buggy line that has been removed.\n```java\n{bug.masked_code}\n```"
        elif mode == "SH":
            return f"The following code contains a buggy hunk that has been removed.\n```java\n{bug.masked_code}\n```"
        elif mode == "SF":
            return f"The following code contains a bug.\n```java\n{bug.code}\n```"
        
    def bug_details(bug: Bug, mode):
        bug_details = "\n".join([
                f"The code fails on this test:\n```\n{bug.test_name}\n```",
                f"on this test line:\n```java\n{bug.test_line}\n```",
                f"with the following test error:\n```\n{bug.test_error_message}\n```"
            ])

        if mode == "SL":
            return "\n".join([f"This was the original buggy line which was removed by the infill location:\n```java\n{bug.buggy_lines}\n```",
                              bug_details])
        elif mode == "SH":
            return "\n".join([f"This was the original buggy hunk which was removed by the infill location:\n```java\n{bug.buggy_lines}\n```",
                              bug_details])
        else:
            return bug_details

    def fpps_call_to_action(mode):
        if mode == "SL":
            return "Please provide the correct line at the infill location."
        elif mode == "SH":
            return "Please provide the correct hunk at the infill location."
        else:
            return "Please provide the correct function."
    
    def mpps_call_to_action(mode):
        if mode == "SL":
            return "Please generate an alternative fix line."
        elif mode == "SH":
            return "Please generate an alternative fix hunk."
        else:
            return "Please generate an alternative fix function."

    def feedback_on_response(bug: Bug, proposed_patch: ProposedPatch):
        if proposed_patch.result_reason == bug.test_error_message:
            return {"role": "user", "content": f"The fixed version is still not correct. It still does not fix the original test failure."}
        else:
            error_type = "test error" if proposed_patch.test_result == "FAIL" else "compilation error"
            return {"role": "user", "content": f"""The fixed version is still not correct. code has the following {error_type}:\n```\n{proposed_patch.result_reason}\n```"""}
    
    def summarize_proposed_patches(ordered_proposed_patches, summary_token_limit):
        included_proposed_patches = []
        summary_message = ""

        while(len(ordered_proposed_patches) > 0):
            proposed_patch = ordered_proposed_patches.pop(-1)

            if any([proposed_patch.patch == included_proposed_patch.patch and proposed_patch.mode == included_proposed_patch.mode for included_proposed_patch in included_proposed_patches]):
                continue
            else:
                included_proposed_patches.append(proposed_patch)

            sorted_proposed_patches = {}
            for included_proposed_patch in included_proposed_patches:
                if included_proposed_patch.result_reason in sorted_proposed_patches:
                    sorted_proposed_patches[included_proposed_patch.result_reason].append(included_proposed_patch)
                else:
                    sorted_proposed_patches[included_proposed_patch.result_reason] = [included_proposed_patch]

            next_summary_message = ""
            for result_reason, proposed_patch_list in sorted_proposed_patches.items():
                mode_solution_name = "line" if proposed_patch_list[0].mode == "SL" else "hunk" if proposed_patch_list[0].mode == "SH" else "function"
                s = "" if (proposed_patch_list) == 1 else "s"
                next_summary_message += "\n".join([
                    f"The following {mode_solution_name}{s}:",
                    "\n".join([f"```java\n{proposed_patch.patch}\n```" for proposed_patch in proposed_patch_list]),
                    f"Failed with the following test error:" if proposed_patch_list[0].test_result == "FAIL" else f"Failed with the following compilation error:",
                    f"```\n{result_reason}\n```",
                ])

            if get_token_count(next_summary_message) > summary_token_limit:
                break
            else:
                summary_message = next_summary_message

        return summary_message

    def summarize_plausible_patches(plausible_patches, summary_token_limit):
        mode = plausible_patches[0].mode

        included_patches = []
        summary_message = ""

        for plausible_patch in plausible_patches.reverse():

            included_patches.append(plausible_patch)
            listed_plausible_patches = "\n".join([f"""{i+1}. ```java\n{pp.patch}\n```""" for i, pp in enumerate(included_patches)])

            s = "s" if len(included_patches) > 1 else ""
            if mode == "SL":
                summary_message = "\n".join([f"It can be fixed by these possible line{s}:", listed_plausible_patches])
            elif mode == "SH":
                summary_message = "\n".join([f"It can be fixed by the following hunk{s}:", listed_plausible_patches])
            elif mode == "SF":
                summary_message = "\n".join([f"It can be fixed by the following function{s}:", listed_plausible_patches])

            if get_token_count(summary_message) > summary_token_limit:
                break
            
        return summary_message

    # RapidCapr Prompts

    def construct_fpps_prompt(bug: Bug, mode, proposed_patches: ProposedPatches, n_shot_bugs, prompt_token_limit, total_token_limit_target):

        if proposed_patches.length(mode=mode) == 0:
            prompt = Prompts.initial_fpps_prompt(bug=bug, mode=mode, n_shot_bugs=n_shot_bugs)
        else:
            prompt = Prompts.ongoing_fpps_prompt(bug=bug, mode=mode, proposed_patches=proposed_patches, prompt_token_limit=prompt_token_limit)
        
        num_of_samples = count_num_of_samples(bug=bug, prompt=prompt, proposed_patches=proposed_patches, mode=mode, total_token_limit_target=total_token_limit_target)

        return prompt, num_of_samples
    
    def initial_fpps_prompt(bug: Bug, mode, n_shot_bugs):
        system_message = Prompts.system_message()

        user_message = "\n".join([Prompts.n_shot_example_message(bug=bug, n_shot_bugs=n_shot_bugs, mode=mode),
                                  Prompts.code_introduction_message(bug=bug, mode=mode),
                                  Prompts.bug_details(bug=bug, mode=mode),
                                  Prompts.fpps_call_to_action(mode=mode)])
            
        return [{"role": "system", "content": system_message}, 
                {"role": "user", "content": user_message}]
    
    def ongoing_fpps_prompt(bug: Bug, mode, proposed_patches: ProposedPatches, prompt_token_limit):
        ordered_proposed_patches = proposed_patches.order(mode=mode)

        system_message = Prompts.system_message()
        last_proposed_patch = ordered_proposed_patches.pop(-1)
        last_assistant_response_message = last_proposed_patch.response
        user_feedback_message = "\n".join([Prompts.feedback_on_response(bug=bug, proposed_patch=last_proposed_patch), Prompts.fpps_call_to_action(mode)]) 
        
        user_message = "\n".join([Prompts.code_introduction_message(bug=bug, mode=mode),Prompts.bug_details(bug=bug, mode=mode), Prompts.fpps_call_to_action(mode=mode)])
        summary_token_limit = prompt_token_limit - get_token_count(system_message) - get_token_count(user_message) - get_token_count(last_assistant_response_message) - get_token_count(user_feedback_message)
        
        proposed_patches_summary = Prompts.summarize_proposed_patches(ordered_proposed_patches=ordered_proposed_patches, summary_token_limit=summary_token_limit)
        user_message = "\n".join([Prompts.code_introduction_message(bug=bug, mode=mode),
                                  Prompts.bug_details(bug=bug, mode=mode),
                                  proposed_patches_summary,
                                  Prompts.fpps_call_to_action(mode=mode)])
        
        return [{"role": "system", "content": system_message}, 
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": last_assistant_response_message},
                {"role": "user", "content": user_feedback_message}]
    
    def construct_mpps_prompt(bug: Bug, mode, proposed_patches: ProposedPatches, n_shot_bugs, prompt_token_limit, total_token_limit_target):
        prompt = Prompts.ongoing_mpps_prompt(bug=bug, mode=mode, proposed_patches=proposed_patches, prompt_token_limit=prompt_token_limit)

        num_of_samples = count_num_of_samples(bug=bug, prompt=prompt, proposed_patches=proposed_patches, mode=mode, total_token_limit_target=total_token_limit_target)

        return prompt, num_of_samples
    
    def ongoing_mpps_prompt(bug: Bug, mode, proposed_patches: ProposedPatches, prompt_token_limit):
        
        user_message = "\n".join([Prompts.code_introduction_message(bug=bug, mode=mode), Prompts.bug_details(bug=bug, mode=mode), Prompts.mpps_call_to_action(mode=mode)])
        summary_token_limit = prompt_token_limit - get_token_count(user_message)

        plausible_patch_summary = Prompts.summarize_plausible_patches(plausible_patches=proposed_patches.get_plausible_patches(mode), summary_token_limit=summary_token_limit)
        
        user_message = "\n".join([Prompts.code_introduction_message(bug=bug, mode=mode),
                            Prompts.bug_details(bug=bug, mode=mode), 
                            plausible_patch_summary, 
                            Prompts.mpps_call_to_action(mode=mode)])

        return [{"role": "system", "content": "You are an automated program repair tool."},
                {"role": "user", "content": f"{user_message}"}]

