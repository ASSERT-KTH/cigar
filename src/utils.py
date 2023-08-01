import tiktoken as tt
from difflib import SequenceMatcher
from itertools import combinations
from src.proposed_patches import ProposedPatches
from src.bug import Bug
from prog_params import ProgParams as prog_params


def extract_patches_from_response(bug: Bug, response, response_mode, similarity_threshold):

    patches = []

    if "```java" in response:

        code_blocks_in_response = response.count("```java")
        for _ in range(code_blocks_in_response):
            patch_block = response[response.find("```java")+len("```java")+1:]
            patch_block = patch_block[:patch_block.find("\n```")]
            patches.append((patch_block, response_mode))
            
            patch = synthetize_and_extract_patch(patch_block=patch_block, masked_code=bug.masked_code, buggy_lines=bug.buggy_lines)
            patches.append((patch, response_mode)) if patch not in [p[0] for p in patches] else None

            if response_mode != "SF":
                buggy_function_and_patch_similarity = similarity(bug.code, patch_block)
                if (buggy_function_and_patch_similarity > similarity_threshold):
                    patches.append((patch_block, "SF"))

            response = response[response.find("\n```")+len("\n```")+1:]

    else:
        patches.append((response, response_mode))

    return patches


def synthetize_and_extract_patch(patch_block, masked_code, buggy_lines):
    masked_code_lines = masked_code.split('\n')
    
    infill_line_count = 0
    for i in range(len(masked_code_lines)):
        if 'INFILL' in masked_code_lines[i]:
            infill_line_count = i
            break

    patch_block_num_of_lines = len(patch_block.split('\n'))

    pre_infill_lines = masked_code_lines[max(0,infill_line_count-patch_block_num_of_lines):infill_line_count]
    post_infill_lines = masked_code_lines[infill_line_count+1:min(infill_line_count+patch_block_num_of_lines+1, len(masked_code_lines))]

    buggy_code_block_lines = pre_infill_lines + [buggy_lines] + post_infill_lines
    buggy_code_block = '\n'.join(buggy_code_block_lines)

    synthetized_code_lines = None
    synthesized_code_similarity = 0
    r = min((patch_block_num_of_lines - 1) * 2 + 1, len(buggy_code_block_lines))

    for synthetized_candidate_lines in [c for c in combinations(pre_infill_lines + [patch_block] + post_infill_lines, r) if patch_block in c]:
        synthesized_candidate_code = '\n'.join(synthetized_candidate_lines)
        candidate_similarity = similarity(buggy_code_block, synthesized_candidate_code)
        if candidate_similarity > synthesized_code_similarity:
            synthesized_code_similarity = candidate_similarity
            synthetized_code_lines = synthetized_candidate_lines

    if synthetized_code_lines is None:
        return patch_block

    patch = '\n'.join(synthetized_code_lines).split('\n')

    for i in range(len(buggy_code_block_lines)):
        if buggy_code_block_lines[i] == patch[0]:
            if len(patch) > 1:
                patch.pop(0)
        else:
            break

    for i in range(len(buggy_code_block_lines)-1, -1, -1):
        if buggy_code_block_lines[i] == patch[-1]:
            if len(patch) > 1:
                patch.pop()
        else:
            break

    for _ in range(len(patch)):
        if patch[0] in buggy_code_block_lines:
            if len(patch) > 0:
                patch.pop(0)
        else:
            break

    for _ in range(len(patch)-1, -1, -1):
        if patch[-1] in buggy_code_block_lines:
            if len(patch) > 0:
                patch.pop()
        else:
            break

    return '\n'.join(patch)


def similarity(a: str, b: str):
    return SequenceMatcher(None, a, b).ratio()


def get_token_count(prompt):
    enc = tt.encoding_for_model(prog_params.gpt35_model)

    if isinstance(prompt, list):
        token_count = 0
        for d in prompt:
            token_count += len(enc.encode(d['content']))

        token_count += len(prompt) * 5 + 3 # Special tokens

        return token_count
    
    if isinstance(prompt, str):
        return len(enc.encode(prompt))


def count_num_of_samples(bug:Bug, prompt, proposed_patches: ProposedPatches, mode, total_token_limit_target):
    prompt_token_count = get_token_count(prompt)
    average_response_token_count = 0
    responses = proposed_patches.get_responses(mode)
    if len(responses) > 0:
        average_response_token_count = int(sum([get_token_count(response) for response in responses]) // len(responses))
    else:
        if mode == "SF":
            average_response_token_count = int(get_token_count(bug.code))
        else:
            average_response_token_count = int(get_token_count(bug.buggy_lines) + get_token_count(bug.code) // 10)
    if average_response_token_count < 5:
        average_response_token_count = 100

    return int((total_token_limit_target - prompt_token_count) // average_response_token_count)
