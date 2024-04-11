from pathlib import Path
import sys
import subprocess
import json

ROOT = '/home/khashayar/projs/cigar/cigar'
PLAUSIBLE_PATCH_PATH = f'{ROOT}/output/'
HUMAN_EVAL_PATH = f'{ROOT}/human-eval-java'
GUMTREE_JAR = f'{ROOT}/gumtree-spoon-ast-diff.jar'

def count_plausible_patches(tool):
    pathlist = list(p for p in Path(f'{PLAUSIBLE_PATCH_PATH}/humanevaljava_{tool}/plausible_patches/').glob('*.diff'))
    plausible_bugs = {}
    for path in pathlist:
        filename = path.name
        bug = '_'.join(filename.replace('humaneval_', '').replace('.diff', '').split('_')[:-2])
        patch_hash = filename.split('_')[-1].replace('.diff', '')
        requests_with_hash = subprocess.run(['grep', '-Rnw', f'{ROOT}/cache/chatgpt_cache/', '-e', f'{patch_hash}'], stdout=subprocess.PIPE)
        min_round, min_try_id = None, None

        if bug in plausible_bugs:
            min_round = plausible_bugs[bug]['min_round']
            min_try_id = plausible_bugs[bug]['min_try_id']

        for line in requests_with_hash.stdout.decode('utf-8').split('\n'):
            if line:
                round, try_id = line.split('/')[-1].split('_patch_hashes')[0].split('_')[-2:]
                round, try_id = int(round[1:]), int(try_id)
                if min_round is None or int(round) < min_round or (round == min_round and try_id < min_try_id):
                    min_round = round
                    min_try_id = try_id
        plausible_bugs[bug] = {'plausible_diff': filename, 'min_round': min_round, 'min_try_id': min_try_id}
    
    print(len(plausible_bugs.keys()))

    with open('humaneval-CigaR-plausible.json', 'w') as fp:
        json.dump(plausible_bugs, fp)

def main(argv):
    count_plausible_patches(argv[0])

if __name__ == '__main__':
    main(sys.argv[1:])
