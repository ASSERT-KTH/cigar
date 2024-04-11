from pathlib import Path
import sys
import matplotlib.pylab as plt
from matplotlib_venn import venn2, venn2_circles, venn3, venn3_circles
import json

ROOT = '/home/khashayar/projs/cigar/cigar'
OUTPUT_PATH = f'{ROOT}/output/'
HUMAN_EVAL_PATH = f'{ROOT}/human-eval-java'

def compute_overlapping_exact_matches():
    only_capr, only_cigar, both = extract_matches_overlap()
    print(f'Only Capr: {len(only_capr)} Only Cigar: {len(only_cigar)} Both: {len(both)}')

    v = venn2(subsets=(46, 13, 125), set_labels=('CigaR', 'ChatRepair'))
    circles = venn2_circles(subsets=(46, 13, 125), linestyle='dashed', linewidth=2)
    v.get_label_by_id('A').set_x(-0.2)
    v.get_label_by_id('A').set_y(-0.55)
    v.get_label_by_id('B').set_x(0.55)
    v.get_label_by_id('B').set_y(-0.2)
    plt.savefig(f'output/summaries/exact_match_venn.pdf')
    plt.show()

def extract_matches_overlap():
    capr_matches = set(json.load(open(f'{ROOT}/humaneval-Capr-matches.json')).keys())
    cigar_matches = set(json.load(open(f'{ROOT}/humaneval-RapidCapr-matches.json')).keys())
    only_capr = capr_matches.difference(cigar_matches)
    only_cigar = cigar_matches.difference(capr_matches)
    both = capr_matches.intersection(cigar_matches)
    return only_capr,only_cigar,both

def compute_cost():
    only_capr, only_cigar, both = extract_matches_overlap()
    pathlist = list(p for p in Path(f'{ROOT}/cache/chatgpt_cache/').glob('*.json'))
    costs = {'cigar': {'only_capr': 0, 'only_cigar': 0, 'both': 0, 'none': 0, 'total': 0},
             'capr': {'only_capr': 0, 'only_cigar': 0, 'both': 0, 'none': 0, 'total': 0}}
    for p in pathlist:
        filename = p.name

        if 'patch_hashes' in p.name:
            continue

        # if not filename.startswith('humanevaljava'):
        #     continue

        bug = '_'.join(filename.split('_')[2:-3])

        try:
            data = json.load(open(p))
        except:
            continue

        if 'response' in data and 'usage' in data['response'] and 'total_tokens' in data['response']['usage']:
            cost = json.load(open(p))['response']['usage']['total_tokens']
        else:
            cost = 0
        
        prompt_type = filename.split('_')[-3]
        tool = 'cigar' if prompt_type.startswith('R') else 'capr'
        if bug in only_capr:
            costs[tool]['only_capr'] += cost
        elif bug in only_cigar:
            costs[tool]['only_cigar'] += cost
        elif bug in both:
            costs[tool]['both'] += cost
        else:
            costs[tool]['none'] += cost

        costs[tool]['total'] += cost

    with open('cost-analysis.json', 'w') as fp:
        json.dump(costs, fp)

def main(argv):
    compute_cost()

if __name__ == '__main__':
    main(sys.argv[1:])
