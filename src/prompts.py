from src.bug import Bug

class Prompts(object):

    def construct_initial_message(bug: Bug, mode: str, n_shot_bugs=None):
        n_shot_examples_text = ""
        if n_shot_bugs:
            for i, bug in enumerate(n_shot_bugs):
                n_shot_initial_prompt = Prompts.construct_initial_message(bug, mode, n_shot_bugs=None)
                if mode == "SL":
                    n_shot_examples_text += f"{n_shot_initial_prompt}\nIt can be fixed by these possible lines:\n1. ```java\n{bug.fixed_lines}\n```\n"
                elif mode == "SH":
                    n_shot_examples_text += f"{n_shot_initial_prompt}\nIt can be fixed by the following hunk:1. ```java\n{bug.fixed_lines}\n```\n"
                elif mode == "SF":
                    n_shot_examples_text += f"{n_shot_initial_prompt}\nIt can be fixed by the following function:1. ```java\n{bug.fixed_code}\n```\n"

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
        return {"role": "user", "content": f"""The fixed version is still not correct. code has the following {error_type}:```\n{result_reason}\n```\n{call_to_action}"""}
    
    def test_fail_feedback():
        return {"role": "user", "content": f"The fixed version is still not correct.It still does not fix the original test failure."}

    def construct_plausable_path_prompt(bug: Bug, plausible_patches, mode: str):

        initial_prompt_message = Prompts.construct_initial_message(bug, mode, n_shot_bugs=None)

        plausible_patches = ""
        for i, patch in enumerate(plausible_patches):
            plausible_patches += f"""{i+1}. ```java\n{patch}\n```\n"""

        s = "s" if len(plausible_patches) > 1 else ""

        if mode == "SL":
            more_plausible_patches_text = f"It can be fixed by these possible line{s}:\n{plausible_patches}Please generate an alternative fix line."
        elif mode == "SH":
            more_plausible_patches_text = f"It can be fixed by the following hunk{s}:\n{plausible_patches}Please generate an alternative fix hunk."
        elif mode == "SF":
            more_plausible_patches_text = f"It can be fixed by the following function{s}:\n{plausible_patches}Please generate an alternative fix function."

        return [{"role": "system", "content": "You are an automated program repair tool."},
                {"role": "user", "content": f"{initial_prompt_message}\n{more_plausible_patches_text}"}]