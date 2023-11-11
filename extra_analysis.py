import os
import logging
import json
from pathlib import Path
from prog_params import ProgParams as prog_params

def main():
    compute_round_distinct_hashes()

def compute_round_distinct_hashes():
    patch_hash_to_test_res = get_patch_hash_to_test_result()

    previous_hashes = set()
    round_info = {}
    total_cost = 0
    total_distinct_plausible = 0
    total_distinct = 0
    pathlist = Path(prog_params.gpt35_cache_folder).glob('**/*.json')
    for path in pathlist:
        path_in_str = str(path)
        if not path_in_str.endswith(".json") or '_R' not in path_in_str or not 'patch_hashes' in path_in_str:
            continue
        proj = path_in_str.split('/')[-1].split("_")[1]
        bug_id = path_in_str.split('/')[-1].split("_")[2]

        round = int(path_in_str.split('_R')[1].split('_')[0])
        trycnt = int(path_in_str.split('_R')[1].split('_')[1])
        current_hashes = set(json.load(open(path_in_str, 'r'))['patch_hashes'])
        distinct_hashes = current_hashes.difference(previous_hashes)
        current_cost = int(json.load(open(path_in_str.replace('_patch_hashes', ''), 'r'))['response']['usage']['total_tokens'])
        total_cost += current_cost

        distinct_plausible_hashes = set(h for h in distinct_hashes if patch_hash_to_test_res[(proj, bug_id, h)] == 'PASS')
        total_distinct_plausible += len(distinct_plausible_hashes)
        total_distinct += len(distinct_hashes)

        round_info[f'round: {round}, trycount: {trycnt}'] = {'distinct_hashes': len(distinct_hashes), 
                                                             'distinct_plausible_hashes': len(distinct_plausible_hashes), 
                                                             'current_cost': current_cost, 'total_distinct': total_distinct, 
                                                             'total_distinct_plausible': total_distinct_plausible, 'total_cost': total_cost}
    
    with open(f'output/defects4j_RapidCapr/rounds_info.json', "w") as file:
                    json.dump(round_info, file,  indent=4, sort_keys=True)


def get_patch_hash_to_test_result():
    ret = {}
    pathlist = Path(prog_params.validate_patch_cache_folder).glob('**/*.json')
    for path in pathlist:
        path_in_str = str(path)
        if not path_in_str.endswith(".json"):
            continue

        proj = path_in_str.split('/')[-1].split("_")[1]
        bug_id = path_in_str.split('/')[-1].split("_")[2]
        hash = path_in_str.split('/')[-1].split("_")[-1].split(".")[0]

        ret[(proj, bug_id, hash)] = json.load(open(path_in_str, 'r'))['test_result']
    
    return ret

def compute_round_exact_matches():
    round_to_bug = {}
    round_to_fixed_bugs = {}
    pathlist = Path(prog_params.gpt35_cache_folder).glob('**/*.json')
    for path in pathlist:
        path_in_str = str(path)
        if not path_in_str.endswith(".json") or not '_R' in path_in_str:
            continue
        round = int(path_in_str.split('_R')[1].split('_')[0])
        bug_proj = path_in_str.split('_R')[0].split('_')[-2]
        bug_id = path_in_str.split('_R')[0].split('_')[-1]
        if round not in round_to_bug:
            round_to_bug[round] = set()
        round_to_bug[round].add((bug_proj, bug_id))

    for i in range(1, 14):
        round_to_fixed_bugs[i] = set()

    with open(f'output/defects4j_RapidCapr/exact_match.csv', "r") as file:
        lines = file.readlines()
        for line in lines[1:]:
            bug_proj = line.split(',')[0]
            bug_id = line.split(',')[1]
            for i in reversed(range(1, 14)):
                round_to_fixed_bugs[i].add((bug_proj, bug_id))
                if (bug_proj, bug_id) in round_to_bug[i]:
                    break
    
    for (round, fixed_bugs) in round_to_fixed_bugs.items():
        print(f"Round {round}: {len(fixed_bugs)},{float(len(fixed_bugs))/float(267)}")

if __name__ == '__main__':
    main()
