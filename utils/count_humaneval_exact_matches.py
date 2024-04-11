from pathlib import Path
import os
import json
import subprocess

ROOT = '/home/khashayar/projs/cigar/cigar'
PLAUSIBLE_PATCH_PATH = f'{ROOT}/output/humanevaljava_RapidCapr/plausible_patches'
HUMAN_EVAL_PATH = f'{ROOT}/human-eval-java'
GUMTREE_JAR = f'{ROOT}/gumtree-spoon-ast-diff.jar'

def check_plausible_patches():
    pathlist = list(p for p in Path(PLAUSIBLE_PATCH_PATH).glob('*.diff'))
    matched_bugs = {}
    print(PLAUSIBLE_PATCH_PATH)
    for path in pathlist:
        filename = path.name
        bug = '_'.join(filename.replace('humaneval_', '').replace('.diff', '').split('_')[:-2])
        # if bug in matched_bugs:
        #     continue
        correct_code_path = str(Path(HUMAN_EVAL_PATH) / 'src/main/java/humaneval/correct/' / f'{bug}.java')
        buggy_code_path = correct_code_path.replace('/correct/', '/buggy/')
        ast_diff_path = f'{path.with_suffix(".ast")}'
        os.system(f'cp {path} {HUMAN_EVAL_PATH}/patch.diff')
        with open(f'{HUMAN_EVAL_PATH}/patch.diff', 'a') as f:
            f.write('\n')
        os.chdir(HUMAN_EVAL_PATH)
        os.system('git reset HEAD --hard')
        os.system('git apply --reject --whitespace=fix patch.diff')
        os.chdir(ROOT)
        os.system(f'java -jar {GUMTREE_JAR} {buggy_code_path} {correct_code_path} > {ast_diff_path}')

        with open(ast_diff_path, 'r') as f:
            diff_lines = f.readlines()
            if len(diff_lines) == 1 and 'no AST change' in diff_lines[0]:
                print(f'No diff found for {filename}')
                patch_hash = filename.split('_')[-1].replace('.diff', '')
                requests_with_hash = subprocess.run(['grep', '-Rnw', f'{ROOT}/cache/chatgpt_cache/', '-e', f'{patch_hash}'], stdout=subprocess.PIPE)
                min_round, min_try_id = None, None

                if bug in matched_bugs:
                    min_round = matched_bugs[bug]['min_round']
                    min_try_id = matched_bugs[bug]['min_try_id']

                for line in requests_with_hash.stdout.decode('utf-8').split('\n'):
                    if line:
                        round, try_id = line.split('/')[-1].split('_patch_hashes')[0].split('_')[-2:]
                        round, try_id = int(round[1:]), int(try_id)
                        if min_round is None or int(round) < min_round or (round == min_round and try_id < min_try_id):
                            min_round = round
                            min_try_id = try_id
                matched_bugs[bug] = {'matching_file': filename, 'min_round': min_round, 'min_try_id': min_try_id}

        print(len(matched_bugs.keys()))

    with open('humaneval-Capr-matches.json', 'w') as fp:
        json.dump(matched_bugs, fp)

def main():
    check_plausible_patches()

if __name__ == '__main__':
    main()
