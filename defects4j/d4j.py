from pathlib import Path
from subprocess import PIPE, run

class Defects4J(object):
    def __init__(self):
        self.d4j_path = "/Users/davidhidvegi/Desktop/defects4j/framework/bin"
        self.tmp_dir = "/tmp/defects4j"
        self.bug_dataset = [
            {"id": "Lang_1", "project": "Lang", "bug_id": 1, "description": "NPE in StringUtils"},
        ]

    def reproduce_bug(self):
        folder = Path(__file__).parent

        project = "Lang"
        bug_id = 25

        work_dir = f"{self.tmp_dir}/{project}-{bug_id}"

        command = ['sh', f'{folder}/reproduce_bug.sh', f"{project}", f"{bug_id}", f"{work_dir}", f"{self.d4j_path}"]
        result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        assert result.returncode == 0

        command = ['sh', f'{folder}/extract_failing_tests.sh', f"{project}", f"{bug_id}", f"{work_dir}", f"{self.d4j_path}"]
        result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        assert result.returncode == 0
        print(result.stdout, result.stderr)

d4j = Defects4J()
d4j.reproduce_bug()