import pandas as pd
from difflib import SequenceMatcher
import json
from pathlib import Path
from subprocess import PIPE, run

def main():
    bug_details_cache_folder = Path(__file__).parent.parent / "cache" / "bug_details_cache"

    output_folder = Path(__file__).parent.parent / "output" / "defects4j_Capr"
    plausible_patch_folder = output_folder / "plausible_patches"
    fixed_patch_folder = output_folder / "fixed_patches"

    ground_truth_fixed_patch_folder = Path(__file__).parent.parent / "output" / "defects4j_RapidCapr" / "fixed_patches"

    plausible_patch_files = list(plausible_patch_folder.glob("*.diff"))
    plausible_bugs = sorted(list(set([f"{f.stem.split('_')[0]}_{f.stem.split('_')[1]}"  for f in plausible_patch_files])), key=lambda x: (x.split('_')[0], int(x.split('_')[1])))
    fixed_patch_files = list(fixed_patch_folder.glob("*.diff"))
    fixed_bugs = sorted(list(set([f"{f.stem.split('_')[0]}_{f.stem.split('_')[1]}"  for f in fixed_patch_files])), key=lambda x: (x.split('_')[0], int(x.split('_')[1])))
    ground_truth_fixed_patch_files = list(ground_truth_fixed_patch_folder.glob("*.diff"))
    
    remaining_bugs = [bug for bug in plausible_bugs if bug not in fixed_bugs]
    # for bug in remaining_bugs:
    #     bug_details = json.load(open(bug_details_cache_folder / f"{bug.split('_')[0]}-{bug.split('_')[1]}.json", "r"))
    #     plausible_patch_diffs_of_bug = [(f, open(f, "r").read()) for f in plausible_patch_files if f"{f.stem.split('_')[0]}_{f.stem.split('_')[1]}" == bug]
        
    #     ground_truth_exists = False
    #     ground_truth_fixed_patch_diffs = [open(f, "r").read() for f in ground_truth_fixed_patch_files if f"{f.stem.split('_')[0]}_{f.stem.split('_')[1]}" == bug]

    #     for file, diff in plausible_patch_diffs_of_bug:
    #         if diff in ground_truth_fixed_patch_diffs:
    #             run(["cp", file, f"{fixed_patch_folder}/"])
    #             ground_truth_exists = True
    #             break

    #     if not ground_truth_exists:
    #         label_bug(bug_details=bug_details, plausible_patch_diffs_of_bug=plausible_patch_diffs_of_bug, fixed_patch_folder=fixed_patch_folder)

    fixed_patch_files = list(fixed_patch_folder.glob("*.diff"))
    update_summaries(output_folder, fixed_patch_files)

def label_bug(bug_details, plausible_patch_diffs_of_bug, fixed_patch_folder):
    plausible_patch_diffs_of_bug = [(f, d) for f, d in plausible_patch_diffs_of_bug]
    ordered_plausible_patch_diffs_of_bug = sorted(plausible_patch_diffs_of_bug, key=lambda x: max(similarity(x[1], bug_details["fixed_lines"]), 
                                                                                                  similarity(x[1], bug_details["fixed_code"])), reverse=True)

    MARK_FIXED = "mark fixed"
    NEXT_PATCH = "next patch"
    PREVIOUS_PATCH = "previous patch"
    GET_FIXED_LINES = "get fixed lines"
    GET_MASKED_CODE = "get masked code"
    GET_PATCH_NAME = "get patch name"
    HELP = "help"
    SKIP_BUG = "skip bug"
    commands = [MARK_FIXED, NEXT_PATCH, PREVIOUS_PATCH, GET_FIXED_LINES, GET_MASKED_CODE, GET_PATCH_NAME, HELP, SKIP_BUG]

    i = 0
    print("".join([f"\n" for _ in range(50)]))
    print(f"\033[93m" + f"\nA proposed diff ({i+1}/{len(plausible_patch_diffs_of_bug)}) is for {bug_details['project']}-{bug_details['bug_id']} ({bug_details['bug_type']}):\n" + "\033[0m")
    print(f"{ordered_plausible_patch_diffs_of_bug[i][1]}")
    while(True):
        command = input("\nCommand: ")
        interpreted_input = sorted([(similarity(command, c), c) for c in commands], key=lambda x: x[0], reverse=True)[0]
        command = interpreted_input[1]
        probability = interpreted_input[0]

        if probability < 0.5:
            command = "help"

        if command == MARK_FIXED:
            print("Marking bug as fixed...")
            plausible_patch_name=ordered_plausible_patch_diffs_of_bug[i][0]
            run(["cp", plausible_patch_name, f"{fixed_patch_folder}/" ])
            print("Done.")
            break
        elif command == NEXT_PATCH:
            i += 1
            print(f"\033[93m" + f"\nAnother proposed diff ({i+1}/{len(plausible_patch_diffs_of_bug)}) is for {bug_details['project']}-{bug_details['bug_id']} ({bug_details['bug_type']}):\n" + "\033[0m")
            print(f"{ordered_plausible_patch_diffs_of_bug[i][1]}")
        elif command == PREVIOUS_PATCH:
            i -= 1
            print(f"\033[93m" + f"\nAnother proposed diff ({i+1}/{len(plausible_patch_diffs_of_bug)}) is for {bug_details['project']}-{bug_details['bug_id']} ({bug_details['bug_type']}):\n" + "\033[0m")
            print(f"{ordered_plausible_patch_diffs_of_bug[i][1]}")
        elif command == GET_FIXED_LINES:
            print(f"\033[93m" + "\nThe correct fix is:\n" + "\033[0m")
            print(f"\033[92m" + bug_details["fixed_lines"] + "\033[0m\n")
        elif command == GET_MASKED_CODE:
            print(f"\033[93m" + "\nThe masked code is:\n" + "\033[0m")
            print(f"{bug_details['masked_code']}")
        elif command == HELP:
            print(f"\033[93m" + "\nThe available commands are:\n" + "\033[0m")
            print(f"{commands}")
        elif command == GET_PATCH_NAME:
            print(f"\033[93m" + "\nThe patch name is:\n" + "\033[0m")
            print(f"{ordered_plausible_patch_diffs_of_bug[i][0]}")
        elif command == SKIP_BUG:
            break

def similarity(a: str, b: str):
    return SequenceMatcher(None, a, b).ratio()

def update_summaries(output_folder, fixed_patch_files):
    for fixed_patch_file in fixed_patch_files:
        project = fixed_patch_file.stem.split("_")[0]
        bug_id = fixed_patch_file.stem.split("_")[1]

        summary_csv = output_folder / f"{project}_summary.csv"
        
        if summary_csv.exists():
            summary = pd.read_csv(summary_csv, dtype=object)
            if summary.loc[(summary["project"] == project) & (summary["bug_id"] == bug_id), "comment"].values[0] != "Fixed Patch":
                summary.loc[(summary["project"] == project) & (summary["bug_id"] == bug_id), "comment"] = "Fixed Patch"
            summary.to_csv(summary_csv, index=False)

if __name__ == "__main__":
    main()
