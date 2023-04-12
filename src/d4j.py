from pathlib import Path
import subprocess
from subprocess import PIPE, run
from framework import Framework

class Defects4J(Framework):
    def __init__(self):
        self.d4j_path = "/Users/davidhidvegi/Desktop/defects4j/framework/bin"
        self.tmp_dir = "/tmp/defects4j"
        self.bug_dataset = [
            {"id": "Lang_1", "project": "Lang", "bug_id": 1, "description": "NPE in StringUtils"},
        ]

    def reproduce_bug(self, bug_id):
        folder = Path(__file__).parent

        project = "Lang"
        # bug_id = 1

        command = ['sh', f'{folder}/test.sh', f"{project}", f"{bug_id}", f"{self.tmp_dir}", f"{self.d4j_path}"]
        result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        print(result.returncode, result.stdout, result.stderr)

        assert result.returncode == 0

d4j = Defects4J()
d4j.reproduce_bug(3)
d4j.reproduce_bug(4)
d4j.reproduce_bug(5)