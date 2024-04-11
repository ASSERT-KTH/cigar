import json
import matplotlib.pyplot as plt
from pathlib import Path
from prog_params import ProgParams as prog_params
from matplotlib.ticker import MaxNLocator

ROUND_INFO_FILE = f'output/defects4j_RapidCapr/rounds_info.json'
SELECTED_ROUND_INFO_FILE = f'output/defects4j_RapidCapr/selected_rounds_info.json'
SELECTED_BUGS_FILE = f'output/defects4j_RapidCapr/selected_bugs.txt'
FIRST_PLAUSIBLE_DATA_FILE = f'output/defects4j_RapidCapr/first_plausible_data.json'

def main():
    # plot_selected_round_info([('Lang', '21'), ('Math', '85'), ('Lang', '31'), ('Lang', '19')])
    plot_selected_round_info(json.load(open(SELECTED_BUGS_FILE, 'r')))
    # compute_selected_rounds_info()

def select_bugs():
    first_plausible_try = list(json.load(open(FIRST_PLAUSIBLE_DATA_FILE, 'r')).items())
    sf_bug_len = sf_bug_to_len()
    first_plausible = [(bug, info | {'len': sf_bug_len[bug]}) for (bug, info) in first_plausible_try if bug in sf_bug_len]
    first_plausible.sort(key=lambda x:(x[1]['round'], x[1]['trycount'], x[1]['len']))

    bugs_with_most_tries = []
    for item in filter(lambda item: item[1]['round'] >= 10, first_plausible):
        bugs_with_most_tries.append(item)
    bugs_with_most_tries.sort(key=lambda x:(x[1]['len']))

    first_try_fixed_bugs = list(filter(lambda item: item[1]['round'] == 1 and item[1]['trycount'] == 1, first_plausible))

    bugs_for_amplification_illustrtion = [first_try_fixed_bugs[0], first_try_fixed_bugs[-1], bugs_with_most_tries[0], bugs_with_most_tries[-1]]

    open(SELECTED_BUGS_FILE, 'w').write(
        json.dumps(
            {'first_plausible': {bug: info for (bug, info) in bugs_with_most_tries},
             'amplification': {bug: info for (bug, info) in bugs_for_amplification_illustrtion},}, 
            indent=4, sort_keys=True))

def sf_bug_to_len():
    pathlist = list(str(p) for p in Path(prog_params.bug_details_cache_folder).glob('**/*.json'))
    bug_info = {}
    not_sf_bugs = set()
    for p in reversed(pathlist):
        filename = p.split('/')[-1]
        proj, bug_id = filename.split('.')[0].split('-')
        info = json.load(open(p, 'r'))
        if info['bug_type'] != 'SF':
            continue
        
        bug_info[f'{proj}_{bug_id}'] = len(info['code'])
    
    return bug_info

def plot_selected_round_info(selected_bugs): # list[(proj, bug_id)]
    # fig, mplot = plt.subplots(2)

    for bug in selected_bugs['first_plausible'].items():
        rounds_info, tokens, distinct_hashes, round_end_points = get_cost_and_distinct_hashes([f'{bug[0]}', 'first_plausible'], 
                                                                                              SELECTED_ROUND_INFO_FILE)
        # distinct_hashes = [sum([r['distinct_hashes'] for r in rounds_info[:i+1]]) for i in range(len(rounds_info))]
        # mplot[0].plot(range(1, len(distinct_hashes) + 1), distinct_hashes, label=bug[0], lw=0.5)
        plt.plot(range(1, len(distinct_hashes) + 1), distinct_hashes, label=bug[0], lw=1)
    plt.xlabel('#TRY', fontsize=8)
    plt.ylabel('#TOTAL_DISTINCT_PATCHES', fontsize=8)
    plt.legend(fontsize=6)
    for i in range(1, 13):
        plt.axvline(i * 10, color = 'gray', label = 'axvline - full height', lw=0.1)
    plt.savefig(f'output/defects4j_RapidCapr/plots/total_distinct_first_plausible.pdf')
    plt.show()

    for bug in selected_bugs['amplification'].items():
        # if bug[0] != 'Math_89' and bug[0] != 'Lang_53':
        #     continue
        rounds_info, tokens, distinct_hashes, round_end_points = get_cost_and_distinct_hashes([f'{bug[0]}', 'amplification'], 
                                                                                              SELECTED_ROUND_INFO_FILE)
        # distinct_hashes = [sum([r['distinct_hashes'] for r in rounds_info[:i+1]]) for i in range(len(rounds_info))]
        print(distinct_hashes)
        plt.plot(range(1, len(distinct_hashes) + 1), distinct_hashes, label=bug[0], lw=1)
    plt.xlabel('#TRY', fontsize=8)
    plt.ylabel('#TOTAL_DISTINCT_PATCHES', fontsize=8)
    plt.xticks(range(1, len(distinct_hashes) + 1))
    plt.legend(fontsize=6)
    for i in range(1, 6):
        plt.axvline(i, color = 'gray', label = 'axvline - full height', lw=0.1)
    plt.savefig(f'output/defects4j_RapidCapr/plots/total_distinct_amplification.pdf')
    plt.show()
    
    # mplot[0].set(xlabel='Try', ylabel='#Distinct_Patches')
    # mplot[0].set_title("Plausible_Search")
    # mplot[0].legend()
    # mplot[1].set(xlabel='Try', ylabel='#Distinct_Patches')
    # mplot[1].set_title("Amplification")
    # mplot[1].legend()

    # plt.savefig(f'output/defects4j_RapidCapr/selected_round_info_plot.pdf')
    # plt.show()

def plot_round_distinct_hashes():
    fig, mplot = plt.subplots(2, 2)

    rounds_info, tokens, distinct_hashes, round_end_points = get_cost_and_distinct_hashes(['first_plausible'])
    distinct_hashes = [sum([r['distinct_hashes'] for r in rounds_info[:i+1]]) for i in range(len(rounds_info))]
    mplot[0][0].plot(range(1, len(distinct_hashes) + 1), distinct_hashes, label='First_Plausible')
    # for round_end_point in round_end_points:
    #     mplot[0][0].plot([round_end_point[0]], [round_end_point[1]], "o", markersize=2, color="black")
    mplot[0][0].set(xlabel='Token_Cost', ylabel='#Distinct_Patches')
    mplot[0][0].set_title("Plausible_Search")

    rounds_info, tokens, distinct_hashes, round_end_points = get_cost_and_distinct_hashes(['amplification'])
    rounds_info, tokens, distinct_hashes = rounds_info[:5], tokens[:5], distinct_hashes[:5]
    mplot[0][1].plot(range(1, len(distinct_hashes) + 1), distinct_hashes, label='Amplification')
    for i in range(len(tokens)):
        mplot[0][1].plot([i + 1], [distinct_hashes[i]], "o", markersize=2, color="green")
    mplot[0][1].set(xlabel='Token_Cost', ylabel='#Distinct_Patches')
    mplot[0][1].set_title("Amplification")

    rounds_info, tokens, distinct_hashes, round_end_points = get_cost_and_distinct_hashes(['max_try_bug', 'first_plausible'])
    mplot[1][0].plot(range(1, len(distinct_hashes) + 1), distinct_hashes, label='Max_Try_Bug')
    # for round_end_point in round_end_points:
    #     mplot[1][0].plot([round_end_point[0]], [round_end_point[1]], "o", markersize=2, color="black")
    rounds_info, tokens, distinct_hashes, round_end_points = get_cost_and_distinct_hashes(['no_plausible_bug', 'first_plausible'])
    mplot[1][0].plot(range(1, len(distinct_hashes) + 1), distinct_hashes, label='No_Plausible_Bug')
    # for round_end_point in round_end_points:
    #     mplot[1][0].plot([round_end_point[0]], [round_end_point[1]], "o", markersize=2, color="black")
    mplot[1][0].set(xlabel='Token_Cost', ylabel='#Distinct_Patches')
    mplot[1][0].set_title("Select_Plausible_Search")
    mplot[1][0].legend()

    rounds_info, tokens, distinct_hashes, round_end_points = get_cost_and_distinct_hashes(['min_try_bug', 'amplification'])
    mplot[1][1].plot(range(1, len(distinct_hashes) + 1), distinct_hashes, label='Min_Try_Bug')
    for i in range(len(tokens)):
        mplot[1][1].plot([i + 1], [distinct_hashes[i]], "o", markersize=2, color="green")
    rounds_info, tokens, distinct_hashes, round_end_points = get_cost_and_distinct_hashes(['max_try_bug', 'amplification'])
    mplot[1][1].plot(range(1, len(distinct_hashes) + 1), distinct_hashes, label='Max_Try_Bug')
    for i in range(len(tokens)):
        mplot[1][1].plot([i + 1], [distinct_hashes[i]], "o", markersize=2, color="green")
    mplot[1][1].set(xlabel='Token_Cost', ylabel='#Distinct_Patches')
    mplot[1][1].set_title("Select_Amplification")
    mplot[1][1].legend()

    for ax in mplot.flat:
        ax.set(xlabel='Token_Cost', ylabel='#Distinct_Patches')
    for ax in mplot.flat:
        ax.label_outer()

    plt.savefig(f'output/defects4j_RapidCapr/round_info_plot.pdf')
    plt.show()

def get_cost_and_distinct_hashes(info_types, round_info=ROUND_INFO_FILE):
    info_object = json.load(open(round_info, 'r'))
    for info_type in info_types:
        info_object = info_object[info_type]
    
    rounds_info = list(info_object.values())
    tokens = [sum([r['cost'] for r in rounds_info[:i+1]]) for i in range(len(rounds_info))]
    distinct_hashes = [sum([r['distinct_hashes'] for r in rounds_info[:i+1]]) for i in range(len(rounds_info))]
    # distinct_hashes = [r['distinct_hashes'] for r in rounds_info]
    # distinct_hashes = [r['distinct_hashes'] / float(r['current_hashes']) for r in rounds_info]
    round_end_points = [(tokens[i], distinct_hashes[i]) for i in range(len(rounds_info)) if i == len(rounds_info) - 1 
                        or rounds_info[i]['round'] != rounds_info[i+1]['round']]

    return rounds_info, tokens, distinct_hashes, round_end_points

def compute_rounds_info():
    patch_hash_to_test_res = get_patch_hash_to_test_result()

    considered_bugs = set()
    previous_hashes = set()
    rounds_info = {}
    first_plausible_try_info = {}
    pathlist = list(str(p) for p in Path(prog_params.gpt35_cache_folder).glob('**/*.json') if '_R' in str(p))
    pathlist.sort(key=lambda x: (int(x.split('_R')[1].split('_')[0]), int(x.split('_R')[1].split('_')[1])))
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
                                   'current_hashes': 0,
                                   'cost': 0,
                                   'round': round, 'trycount': trycnt}
        rounds_info[try_id]['distinct_hashes'] += len(distinct_hashes)
        rounds_info[try_id]['distinct_plausible_hashes'] += len(distinct_plausible_hashes)
        rounds_info[try_id]['current_hashes'] += len(current_hashes)
        rounds_info[try_id]['cost'] += current_cost

        proj_bug_id = f'{proj}_{bug_id}'

        rounds_info[f'{try_id}_{proj_bug_id}'] = {'distinct_hashes': len(distinct_hashes),
                                                    'distinct_plausible_hashes': len(distinct_plausible_hashes),
                                                    'current_hashes': len(current_hashes),
                                                    'cost': current_cost,
                                                    'proj': proj, 'bug_id': bug_id,
                                                    'round': round, 'trycount': trycnt}
        
        considered_bugs.add(proj_bug_id)
        
        if (not proj_bug_id in first_plausible_try_info or round < first_plausible_try_info[proj_bug_id]['round'] 
            or (round == first_plausible_try_info[proj_bug_id]['round'] and trycnt < first_plausible_try_info[proj_bug_id]['trycount'])):
            if any(patch_hash_to_test_res[(proj, bug_id, h)] == 'PASS' for h in current_hashes):
                first_plausible_try_info[proj_bug_id] = {'round': round, 'trycount': trycnt}
        
        previous_hashes.update(current_hashes)
    

    rounds_info['first_plausible'] = {}
    rounds_info['amplification'] = {}

    open(FIRST_PLAUSIBLE_DATA_FILE, 'w').write(json.dumps(first_plausible_try_info, indent=4, sort_keys=True))

    first_plausible_try_info_items = list(first_plausible_try_info.items())
    first_plausible_try_info_items.sort(key=lambda x:(x[1]['round'], x[1]['trycount']))    
    min_try_bug = first_plausible_try_info_items[0][0]
    max_try_bug = first_plausible_try_info_items[-1][0]
    median_try_bug = first_plausible_try_info_items[len(first_plausible_try_info_items)//2][0]
    no_plausible_bug = list(considered_bugs.difference(set(first_plausible_try_info.keys())))[0]
    print(f'min_try: {min_try_bug}, max_try: {max_try_bug}, median_try: {median_try_bug}, no_plausible_bug: {no_plausible_bug}')



    round_info_items = list(rounds_info.values())
    for item in round_info_items:
        if not 'proj' in item or not 'bug_id' in item:
            continue

        proj_bug_id = f'{item["proj"]}_{item["bug_id"]}'

        if (not proj_bug_id in first_plausible_try_info 
            or compare_try(item, first_plausible_try_info[proj_bug_id]) <= 0):
            try_type = 'first_plausible'
            try_id = f"r{item['round']:02d}_t{item['trycount']:02d}"
        else:
            try_type = 'amplification'
            try_id = f"t{item['trycount'] - first_plausible_try_info[proj_bug_id]['trycount']}"

        if not try_id in rounds_info[f'{try_type}']:
            rounds_info[f'{try_type}'][try_id] = {'distinct_hashes': 0, 
                                                        'distinct_plausible_hashes': 0,
                                                        'current_hashes': 0,
                                                        'cost': 0,
                                                        'proj': item['proj'], 'bug_id': item['bug_id'],
                                                        'round': item['round'], 'trycount': item['trycount']}
        rounds_info[f'{try_type}'][try_id]['distinct_hashes'] += item['distinct_hashes']
        rounds_info[f'{try_type}'][try_id]['distinct_plausible_hashes'] += item['distinct_plausible_hashes']
        rounds_info[f'{try_type}'][try_id]['current_hashes'] += item['current_hashes']
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
            if selected_bug_type not in rounds_info:
                rounds_info[selected_bug_type] = {}

            if not try_type in rounds_info[selected_bug_type]:
                rounds_info[selected_bug_type][try_type] = {}
            if not try_id in rounds_info[selected_bug_type][try_type]:
                rounds_info[selected_bug_type][try_type][try_id] = {'distinct_hashes': 0, 
                                                                'distinct_plausible_hashes': 0,
                                                                'current_hashes': 0,
                                                                'cost': 0,
                                                                'round': item['round'], 'trycount': item['trycount']}
            rounds_info[selected_bug_type][try_type][try_id]['distinct_hashes'] += item['distinct_hashes']
            rounds_info[selected_bug_type][try_type][try_id]['distinct_plausible_hashes'] += item['distinct_plausible_hashes']
            rounds_info[selected_bug_type][try_type][try_id]['current_hashes'] += item['current_hashes']
            rounds_info[selected_bug_type][try_type][try_id]['cost'] += item['cost']

    
    with open(ROUND_INFO_FILE, "w") as file:
        json.dump(rounds_info, file,  indent=4, sort_keys=True)

def compute_selected_rounds_info(): # list[(proj, bug_id)]
    selected_bugs_info = json.load(open(SELECTED_BUGS_FILE, 'r'))
    selected_bugs = [(bug.split('_')[0], bug.split('_')[1]) for bug, _ in 
                     list(selected_bugs_info['first_plausible'].items())
                     + list(selected_bugs_info['amplification'].items())]

    patch_hash_to_test_res = get_patch_hash_to_test_result()

    pathlist = list(str(p) for p in Path(prog_params.gpt35_cache_folder).glob('**/*.json') if '_R' in str(p))
    rounds_info = {}
    for bug in selected_bugs:
        pathlist_for_bug = [p for p in pathlist if f'_{bug[0]}_{bug[1]}_' in p and int(p.split('_R')[1].split('_')[0]) < 13]
        pathlist_for_bug.sort(key=lambda x: (int(x.split('_R')[1].split('_')[0]), int(x.split('_R')[1].split('_')[1])))

        previous_hashes = set()

        proj = bug[0]
        bug_id = bug[1]
        proj_bug_id = f'{proj}_{bug_id}'

        rounds_info[f'{proj_bug_id}'] = {'first_plausible': {}, 'amplification': {}}

        is_amplification = False

        for path in pathlist_for_bug:
            path = str(path)
            if not path.endswith(".json") or '_R' not in path or not 'patch_hashes' in path:
                continue

            round = int(path.split('_R')[1].split('_')[0])
            trycnt = int(path.split('_R')[1].split('_')[1])
            current_hashes = list(json.load(open(path, 'r'))['patch_hashes'])
            distinct_hashes = set(current_hashes).difference(previous_hashes)
            current_cost = int(json.load(open(path.replace('_patch_hashes', ''), 'r'))['response']['usage']['total_tokens'])
            plausible_hashes = set(h for h in current_hashes if patch_hash_to_test_res[(proj, bug_id, h)] == 'PASS')

            try_id = f"r{round:02d}_t{trycnt:02d}"


            if not is_amplification:
                try_type = 'first_plausible'
            else:
                try_type = 'amplification'    
            
            rounds_info[f'{proj_bug_id}'][f'{try_type}'][f'{try_id}'] = {'distinct_hashes': len(distinct_hashes),
                                                        'current_hashes': len(current_hashes),
                                                        'cost': current_cost,
                                                        'proj': proj, 'bug_id': bug_id,
                                                        'round': round, 'trycount': trycnt}

            previous_hashes.update(current_hashes)

            if len(plausible_hashes) > 0:
                is_amplification = True

        if proj == 'Math' and bug_id == '89':
            with open('tmp.txt', 'a') as file:
                patches = []
                for hash in previous_hashes:
                    patch = json.load(open(f'cache/validate_patch_cache/defects4j_Math_89_SF_{hash}.json', 'r'))['patch']
                    for p in patches:
                        if len(p) == len(patch):
                            file.write(f'Found patch with same length for {hash} with len {len(p)},{len(patch)}: \n {p}\n###\n{patch}\n\n')
                            break
                    patches.append(patch)

    with open(SELECTED_ROUND_INFO_FILE, "w") as file:
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
