from pathlib import Path
import sys

ROOT = '/home/khashayar/projs/cigar/cigar'
PLAUSIBLE_PATCH_PATH = f'{ROOT}/output/'
HUMAN_EVAL_PATH = '{ROOT}/human-eval-java'
GUMTREE_JAR = '{ROOT}/gumtree-spoon-ast-diff.jar'

def count_plausible_patches(tool):
    pathlist = list(p for p in Path(f'{PLAUSIBLE_PATCH_PATH}/humanevaljava_{tool}/plausible_patches/').glob('*.diff'))
    plausible_bugs = set()
    for path in pathlist:
        filename = path.name
        bug = '_'.join(filename.replace('humaneval_', '').replace('.diff', '').split('_')[:-1])
        plausible_bugs.add(bug)
    
    print(len(plausible_bugs))

def main(argv):
    count_plausible_patches(argv[0])

if __name__ == '__main__':
    main(sys.argv[1:])
