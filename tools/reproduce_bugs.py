from pathlib import Path
from subprocess import PIPE, run

test_framework = "defects4j"
tmp_dir = f"/tmp/{test_framework}"
shell_scripts_folder = Path(__file__).parent.parent / "frameworks"
d4j_path = "/Users/davidhidvegi/Desktop/defects4j/framework/bin"

def reproduce_bugs(project=None):
    project = str(project)

    list_of_bugs = [
        ("Chart", [i for i in range(1, 27)]),
        ("Closure", [i for i in range(1, 177) if i != 63 and i != 93]),
        ("Lang", [i for i in range(1, 66) if i != 2]),
        ("Math", [i for i in range(1, 107)]),
        ("Mockito", [i for i in range(1, 39)]), # Failed to reproduce bugs on macOS and Ubuntu
        ("Time", [i for i in range(1, 28) if i != 21])
    ]

    if project != "all":
        list_of_bugs = [l for l in list_of_bugs if l[0] == project]

    for project, ids in list_of_bugs:
        for bug_id in ids:
            work_dir = f"{tmp_dir}/{project}-{bug_id}"

            print(f"Reproducing {project}-{bug_id}")
            run_bash("checkout_bug", work_dir, project, bug_id)
            run_bash("compile_and_run_tests", work_dir, project, bug_id)

def run_bash(function, work_dir, project, bug_id, extra_arg=None):
    command = ['bash', f'{shell_scripts_folder}/{test_framework}.sh', function, f"{project}", f"{bug_id}", f"{work_dir}", f"{d4j_path}", f"{extra_arg}"]
    result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    assert result.returncode == 0
    result.stdout = result.stdout[:-1]
    return result

if __name__ == "__main__":
    import sys
    arg = None
    if (len(sys.argv) > 1):
        arg = Path(sys.argv[1])
    reproduce_bugs(arg)
