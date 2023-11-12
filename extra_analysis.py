import json
import matplotlib.pyplot as plt
from pathlib import Path
from prog_params import ProgParams as prog_params

ROUND_INFO_FILE = f'output/defects4j_RapidCapr/rounds_info.json'

def main():
    compute_round_exact_matches()

def plot_round_distinct_hashes():
    rounds_info = list(json.load(open(ROUND_INFO_FILE, 'r')).values())
    rounds_info.sort(key=lambda x:(x['round'], x['trycount']))
    tokens = [sum([r['cost'] for r in rounds_info[:i+1]]) for i in range(len(rounds_info))]
    distinct_hashes = [sum([r['distinct_hashes'] for r in rounds_info[:i+1]]) for i in range(len(rounds_info))]
    distinct_plausible_hashes = [sum([r['distinct_plausible_hashes'] for r in rounds_info[:i+1]]) for i in range(len(rounds_info))]
    plt.plot(tokens, distinct_hashes, label='#Distinct Hashes')
    plt.plot(tokens, distinct_plausible_hashes, label='#Distinct Plausible Hashes')
    plt.xlabel('Token_Cost')
    plt.ylabel('Distinct Hashes')
    plt.legend()
    plt.show()

def compute_round_distinct_hashes():
    patch_hash_to_test_res = get_patch_hash_to_test_result()

    considered_bugs = set()
    previous_hashes = set()
    rounds_info = {}
    first_plausible_try_info = {}
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

        distinct_plausible_hashes = set(h for h in distinct_hashes if patch_hash_to_test_res[(proj, bug_id, h)] == 'PASS')

        try_id = f"r{round:02d}_t{trycnt:02d}"

        if try_id not in rounds_info:
            rounds_info[try_id] = {'distinct_hashes': 0, 
                                   'distinct_plausible_hashes': 0, 
                                   'cost': 0,
                                   'round': round, 'trycount': trycnt}
        rounds_info[try_id]['distinct_hashes'] += len(distinct_hashes)
        rounds_info[try_id]['distinct_plausible_hashes'] += len(distinct_plausible_hashes)
        rounds_info[try_id]['cost'] += current_cost

        proj_bug_id = f'{proj}_{bug_id}'

        rounds_info[f'{try_id}_{proj_bug_id}'] = {'distinct_hashes': len(distinct_hashes),
                                                    'distinct_plausible_hashes': len(distinct_plausible_hashes),
                                                    'cost': current_cost,
                                                    'proj': proj, 'bug_id': bug_id,
                                                    'round': round, 'trycount': trycnt}
        
        considered_bugs.add(proj_bug_id)
        
        if round < first_plausible_try_info[proj_bug_id]['round'] or (round == first_plausible_try_info[proj_bug_id]['round'] and trycnt < first_plausible_try_info[proj_bug_id]['trycount']):
            if any(patch_hash_to_test_res[(proj, bug_id, h)] == 'PASS' for h in current_hashes):
                first_plausible_try_info[proj_bug_id] = {'round': round, 'trycount': trycnt}
        
        previous_hashes.update(current_hashes)
    

    rounds_info['first_plausible'] = {}
    rounds_info['amplification'] = {}


    first_plausible_try_info_items = first_plausible_try_info.items.sort(key=lambda x:(x[1]['round'], x[1]['trycount']))
    min_try_bug = first_plausible_try_info_items[0][0]
    max_try_bug = first_plausible_try_info_items[-1][0]
    median_try_bug = first_plausible_try_info_items[len(first_plausible_try_info_items)//2][0]
    no_plausible_bug = considered_bugs.difference(set(first_plausible_try_info.keys()))[0]
    print(f'min_try: {min_try_bug}, max_try: {max_try_bug}, median_try: {median_try_bug}')



    for item in rounds_info.values():
        proj_bug_id = f'{item["proj"]}_{item["bug_id"]}'

        if compare_try(item, first_plausible_try_info[proj_bug_id]) <= 0:
            try_type = 'first_plausible'
            try_id = f"r{item['round']:02d}_t{item['trycnt']:02d}"
        else:
            try_type = 'amplification'
            try_id = f"r{item['try'] - first_plausible_try_info[proj_bug_id]['trycnt']}"

        if not try_id in rounds_info[f'{try_type}']:
            rounds_info[f'{try_type}'][try_id] = {'distinct_hashes': 0, 
                                                        'distinct_plausible_hashes': 0, 
                                                        'cost': 0,
                                                        'round': item['round'], 'trycount': item['trycnt']}
        rounds_info[f'{try_type}'][try_id]['distinct_hashes'] += item['distinct_hashes']
        rounds_info[f'{try_type}'][try_id]['distinct_plausible_hashes'] += item['distinct_plausible_hashes']
        rounds_info[f'{try_type}'][try_id]['cost'] += item['cost']

        selected_bug_type = None

        if proj_bug_id == min_try_bug:
            selected_bug_type = 'min_try_bug'
        elif proj_bug_id == max_try_bug:
            selected_bug_type = 'max_try_bug'
        elif proj_bug_id == median_try_bug:
            selected_bug_type = 'median_try_bug'
        elif proj_bug_id == no_plausible_bug:
            selected_bug_type = 'no_plausible_bug'
        
        if selected_bug_type is not None:
            if not try_type in rounds_info[selected_bug_type]:
                rounds_info[selected_bug_type][try_type] = {}
            if not try_id in rounds_info[selected_bug_type][try_type]:
                rounds_info[selected_bug_type][try_type][try_id] = {'distinct_hashes': 0, 
                                                                'distinct_plausible_hashes': 0, 
                                                                'cost': 0,
                                                                'round': item['round'], 'trycount': item['trycnt']}
            rounds_info[selected_bug_type][try_type][try_id]['distinct_hashes'] += item['distinct_hashes']
            rounds_info[selected_bug_type][try_type][try_id]['distinct_plausible_hashes'] += item['distinct_plausible_hashes']
            rounds_info[selected_bug_type][try_type][try_id]['cost'] += item['cost']

    
    with open(ROUND_INFO_FILE, "w") as file:
        json.dump(rounds_info, file,  indent=4, sort_keys=True)

def compare_try(item1, item2):
    if item1['round'] < item2['round']:
        return -1
    elif item1['round'] > item2['round']:
        return 1
    else:
        if item1['trycount'] < item2['trycount']:
            return -1
        elif item1['trycount'] > item2['trycount']:
            return 1
        else:
            return 0

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
