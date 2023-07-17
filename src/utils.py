from difflib import SequenceMatcher
from itertools import combinations


def similarity(a: str, b: str):
    return SequenceMatcher(None, a, b).ratio()


def synthetize_and_extract_patch(patch_block, masked_code, buggy_lines):
    masked_code_lines = masked_code.split('\n')
    
    infill_line_count = None
    for i in range(len(masked_code_lines)):
        if "INFILL" in masked_code_lines[i]:
            infill_line_count = i
            break

    patch_block_num_of_lines = len(patch_block.split('\n'))

    pre_infill_lines = masked_code_lines[infill_line_count-patch_block_num_of_lines:infill_line_count]
    post_infill_lines = masked_code_lines[infill_line_count+1:infill_line_count+patch_block_num_of_lines+1]

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
            patch.pop(0)
        else:
            break

    for i in range(len(buggy_code_block_lines)-1, -1, -1):
        if buggy_code_block_lines[i] == patch[-1]:
            patch.pop()
        else:
            break

    for _ in range(len(patch)):
        if patch[0] in buggy_code_block_lines:
            patch.pop(0)
        else:
            break

    for _ in range(len(patch)-1, -1, -1):
        if patch[-1] in buggy_code_block_lines:
            patch.pop()
        else:
            break

    return '\n'.join(patch)
        