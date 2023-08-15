import pandas as pd
from difflib import SequenceMatcher
import json
from pathlib import Path
from subprocess import PIPE, run

def main():
    bug_details_cache_folder = Path(__file__).parent.parent / "cache" / "bug_details_cache"

    output_folder = Path(__file__).parent.parent / "output" / "defects4j_RapidCapr"
    plausible_patch_folder = output_folder / "plausible_patches"
    fixed_patch_folder = output_folder / "fixed_patches"

    ground_truth_fixed_patch_folder = Path(__file__).parent.parent / "output" / "defects4j_Capr" / "fixed_patches"

    plausible_patch_files = list(plausible_patch_folder.glob("*.diff"))
    plausible_bugs = sorted(list(set([f"{f.stem.split('_')[0]}_{f.stem.split('_')[1]}"  for f in plausible_patch_files])), key=lambda x: (x.split('_')[0], int(x.split('_')[1])))
    fixed_patch_files = list(fixed_patch_folder.glob("*.diff"))
    fixed_bugs = sorted(list(set([f"{f.stem.split('_')[0]}_{f.stem.split('_')[1]}"  for f in fixed_patch_files])), key=lambda x: (x.split('_')[0], int(x.split('_')[1])))
    ground_truth_fixed_patch_files = list(ground_truth_fixed_patch_folder.glob("*.diff"))
    
    remaining_bugs = [bug for bug in plausible_bugs if bug not in fixed_bugs]
    for bug in remaining_bugs:
        bug_details = json.load(open(bug_details_cache_folder / f"{bug.split('_')[0]}-{bug.split('_')[1]}.json", "r"))
        plausible_patch_diffs_of_bug = [(f, open(f, "r").read()) for f in plausible_patch_files if f"{f.stem.split('_')[0]}_{f.stem.split('_')[1]}" == bug]
        
        ground_truth_exists = False
        ground_truth_fixed_patch_diffs = [open(f, "r").read() for f in ground_truth_fixed_patch_files if f"{f.stem.split('_')[0]}_{f.stem.split('_')[1]}" == bug]

        for file, diff in plausible_patch_diffs_of_bug:
            if diff in ground_truth_fixed_patch_diffs:
                run(["cp", file, f"{fixed_patch_folder}/"])
                ground_truth_exists = True
                break

            # Check if ground truth solution is in the diff file
            patch_lines = diff.split("\n")
            patch_additions = [line for line in patch_lines if line.startswith("+")][1:]
            patch_removes = [line for line in patch_lines if line.startswith("-")][1:]
            if len(patch_additions) == 1 and len(patch_removes) == len(bug_details["buggy_lines"].split("\n")):
                patch_addition = patch_additions[0].strip("+").strip()
                if patch_addition in bug_details["fixed_lines"]:
                    run(["cp", file, f"{fixed_patch_folder}/"])
                    ground_truth_exists = True
                    break

        if not ground_truth_exists:
            command = label_bug(bug_details=bug_details, plausible_patch_diffs_of_bug=plausible_patch_diffs_of_bug, fixed_patch_folder=fixed_patch_folder)
            if command == "skip all bugs":
                break

    fixed_patch_files = list(fixed_patch_folder.glob("*.diff"))
    save_fixed_patch_summary(output_folder, fixed_patch_files)

def label_bug(bug_details, plausible_patch_diffs_of_bug, fixed_patch_folder):
    plausible_patch_diffs_of_bug = [(f, d) for f, d in plausible_patch_diffs_of_bug]
    ordered_plausible_patch_diffs_of_bug = sorted(plausible_patch_diffs_of_bug, key=lambda x: max(similarity(x[1], bug_details["fixed_lines"]), 
                                                                                                  similarity(x[1], bug_details["fixed_code"])), reverse=True)

    MARK_FIXED = "mark fixed"
    NEXT_PATCH = "next patch"
    PREVIOUS_PATCH = "previous patch"
    PRINT_RESOLVED_DIFF = "print resolved diff"
    GET_BUGGY_LINES = "get buggy lines"
    GET_FIXED_LINES = "get fixed lines"
    GET_CODE = "get code"
    GET_MASKED_CODE = "get masked code"
    GET_FIXED_CODE = "get fixed code"
    GET_PATCH_NAME = "get patch name"
    HELP = "help"
    SKIP_BUG = "skip bug"
    SKIP_ALL_BUGS = "skip all bugs"
    commands = [MARK_FIXED, NEXT_PATCH, PREVIOUS_PATCH, PRINT_RESOLVED_DIFF, GET_BUGGY_LINES, GET_FIXED_LINES, GET_CODE, GET_FIXED_CODE, GET_MASKED_CODE, GET_PATCH_NAME, HELP, SKIP_BUG, SKIP_ALL_BUGS]

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
            i = (i + 1) % len(plausible_patch_diffs_of_bug)
            print(f"\033[93m" + f"\nAnother proposed diff ({i+1}/{len(plausible_patch_diffs_of_bug)}) is for {bug_details['project']}-{bug_details['bug_id']} ({bug_details['bug_type']}):\n" + "\033[0m")
            print(f"{ordered_plausible_patch_diffs_of_bug[i][1]}")
        elif command == PREVIOUS_PATCH:
            i = (i - 1) % len(plausible_patch_diffs_of_bug)
            print(f"\033[93m" + f"\nAnother proposed diff ({i+1}/{len(plausible_patch_diffs_of_bug)}) is for {bug_details['project']}-{bug_details['bug_id']} ({bug_details['bug_type']}):\n" + "\033[0m")
            print(f"{ordered_plausible_patch_diffs_of_bug[i][1]}")
        elif command == PRINT_RESOLVED_DIFF:
            print(f"\033[93m" + "\nThe resolved diff is:\n" + "\033[0m")
            patch_diff = ordered_plausible_patch_diffs_of_bug[i][1]
            print("\n".join([line[1:] if line.startswith("+") else line for line in patch_diff.split("\n") if not line.startswith("-")]))
        elif command == GET_BUGGY_LINES:
            print(f"\033[93m" + "\nThe buggy lines are:\n" + "\033[0m")
            print(f"\033[91m" + bug_details["buggy_lines"] + "\033[0m\n")
        elif command == GET_FIXED_LINES:
            print(f"\033[93m" + "\nThe correct fix is:\n" + "\033[0m")
            print(f"\033[92m" + bug_details["fixed_lines"] + "\033[0m\n")
        elif command == GET_CODE:
            print(f"\033[93m" + "\nThe code is:\n" + "\033[0m")
            print(f"{bug_details['code']}")
        elif command == GET_MASKED_CODE:
            print(f"\033[93m" + "\nThe masked code is:\n" + "\033[0m")
            print(f"{bug_details['masked_code']}")
        elif command == GET_FIXED_CODE:
            print(f"\033[93m" + "\nThe fixed code is:\n" + "\033[0m")
            print(f"\033[92m" + bug_details["fixed_code"] + "\033[0m\n")
        elif command == HELP:
            print(f"\033[93m" + "\nThe available commands are:\n" + "\033[0m")
            print(f"{commands}")
        elif command == GET_PATCH_NAME:
            print(f"\033[93m" + "\nThe patch name is:\n" + "\033[0m")
            print(f"{ordered_plausible_patch_diffs_of_bug[i][0]}")
        elif command == SKIP_BUG:
            break
        elif command == SKIP_ALL_BUGS:
            return SKIP_ALL_BUGS

def similarity(a: str, b: str):
    return SequenceMatcher(None, a, b).ratio()

def save_fixed_patch_summary(output_folder, fixed_patch_files):
    fixed_patch_files = sorted(fixed_patch_files, key=lambda x: (x.stem.split("_")[0], int(x.stem.split("_")[1])))

    summary_csv_file = output_folder / f"fixed_patch_summary.csv"

    # open summary_csv_file in writing mode and write header
    with open(summary_csv_file, "w") as summary_csv:
        summary_csv.write("project,bug_id,filename\n")

        for fixed_patch_file in fixed_patch_files:
            project = fixed_patch_file.stem.split("_")[0]
            bug_id = fixed_patch_file.stem.split("_")[1]

            summary_csv.write(f"{project},{bug_id},{fixed_patch_file.stem}\n")

if __name__ == "__main__":
    main()
