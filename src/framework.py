import hashlib
import json
from pathlib import Path
from subprocess import PIPE, run
from src.bug import Bug

class Framework(object):
    def __init__(self, test_framework, cache_folder=None):
        assert test_framework in ["defects4j", "quixbugs"]
        self.test_framework = test_framework
        self.cache_folder = cache_folder

        self.d4j_path = "/Users/davidhidvegi/Desktop/defects4j/framework/bin"
        self.tmp_dir = f"/tmp/{test_framework}"
        self.shell_scripts_folder = Path(__file__).parent.parent / "frameworks" / self.test_framework

    def reproduce_bug(self, project, bug_id):

        work_dir = f"{self.tmp_dir}/{project}-{bug_id}"

        self._reproduce_buggy_folder(work_dir, project, bug_id)

        bug_type = self._extract_bug_type(work_dir, project, bug_id)
        if bug_type == "OT":
            return None
        
        test_suite = self._extract_test_suite(work_dir, project, bug_id)
        test_name = self._extract_test_name(work_dir, project, bug_id)
        test_error = self._extract_test_error(work_dir, project, bug_id)
        test_line = self._extract_test_line(work_dir, project, bug_id)
        buggy_line = self._extract_buggy_line(work_dir, project, bug_id)
        fixed_line = self._extract_fixed_line(work_dir, project, bug_id)
        code = self._extract_code(work_dir, project, bug_id)
        masked_code = self._extract_masked_code(work_dir, project, bug_id)
        file_change_count, line_change_count = self._extract_file_and_line_change_count(work_dir, project, bug_id)

        return Bug(test_framework=self.test_framework,
                   project=project,
                   bug_id=bug_id,
                   bug_type=bug_type,
                   file_change_count=file_change_count,
                   line_change_count=line_change_count,
                   code=code,
                   masked_code=masked_code,
                   buggy_line=buggy_line,
                   fixed_line=fixed_line,
                   test_suite=test_suite,
                   test_name=test_name,
                   test_line=test_line,
                   test_error_message=test_error)

    def validate_patch(self, bug: Bug, proposed_line_fix):

        test_result = None
        result_reason = None
        patch_hash = hashlib.md5(str(proposed_line_fix).encode('utf-8')).hexdigest()

        if self.cache_folder is not None:
            cache_file_path = f"{self.cache_folder}/{self.test_framework}_{bug.project}_{bug.bug_id}_{patch_hash}.json"
            if Path(cache_file_path).is_file():
                with open(cache_file_path, "r") as file:
                    json_to_load = json.load(file)
                    test_result = json_to_load['test_result']
                    result_reason = json_to_load['result_reason']

        if test_result is None and result_reason is None:

            project = bug.project
            bug_id = bug.bug_id
            work_dir = f"{self.tmp_dir}/{project}-{bug_id}"

            command = ['bash', f'{self.shell_scripts_folder}/validate_patch.sh', f"{project}", f"{bug_id}", f"{work_dir}", f"{self.d4j_path}", f"{proposed_line_fix}"]
            result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
            
            if result.returncode == 1:
                result_reason = result.stderr
                result_reason = result_reason[result_reason.find("error: "):]
                result_reason = result_reason[:result_reason.find("\n")]

                test_result, result_reason = "ERROR", result_reason # compilation error
            else:
                all_tests_passed = result.stdout.find("Failing tests: 0") != -1

                if all_tests_passed:
                    test_result, result_reason = "PASS", "all tests passed" # test pass
                else:
                    test_result = "FAIL" # test fail
                    result_reason = self._extract_test_error(work_dir, project, bug_id)

        if self.cache_folder is not None:
            with open(cache_file_path, "w") as file:
                json.dump({'patch': proposed_line_fix, 'test_result': test_result, 'result_reason': result_reason}, file,  indent=4, sort_keys=True)

            
        return test_result, result_reason

    def _extract_bug_type(self, work_dir, project, bug_id):
        command = ['bash', f'{self.shell_scripts_folder}/extract_bug_type.sh', f"{project}", f"{bug_id}", f"{work_dir}", f"{self.d4j_path}"]
        result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        assert result.returncode == 0 and len(result.stdout) > 1
        return result.stdout[:-1] # remove new line at the end of result.stdout

    def _reproduce_buggy_folder(self, work_dir, project, bug_id):
        command = ['bash', f'{self.shell_scripts_folder}/reproduce_bug.sh', f"{project}", f"{bug_id}", f"{work_dir}", f"{self.d4j_path}"]
        result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        assert result.returncode == 0

    def _extract_file_and_line_change_count(self, work_dir, project, bug_id):
        command = ['bash', f'{self.shell_scripts_folder}/extract_file_and_line_change_count.sh', f"{project}", f"{bug_id}", f"{work_dir}", f"{self.d4j_path}"]
        result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        assert result.returncode == 0 and len(result.stdout) > 1
        result = result.stdout.split('|')
        return int(result[0]), int(result[1])

    def _extract_test_suite(self, work_dir, project, bug_id):
        command = ['bash', f'{self.shell_scripts_folder}/extract_test_suite.sh', f"{project}", f"{bug_id}", f"{work_dir}", f"{self.d4j_path}"]
        result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        assert result.returncode == 0 and len(result.stdout) > 1
        return result.stdout[:-1] # remove new line at the end of result.stdout
        
    def _extract_test_name(self, work_dir, project, bug_id):
        command = ['bash', f'{self.shell_scripts_folder}/extract_test_name.sh', f"{project}", f"{bug_id}", f"{work_dir}", f"{self.d4j_path}"]
        result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        assert result.returncode == 0 and len(result.stdout) > 1
        return result.stdout[:-1] # remove new line at the end of result.stdout
    
    def _extract_test_error(self, work_dir, project, bug_id):
        command = ['bash', f'{self.shell_scripts_folder}/extract_test_error.sh', f"{project}", f"{bug_id}", f"{work_dir}", f"{self.d4j_path}"]
        result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        assert result.returncode == 0 and len(result.stdout) > 1
        return result.stdout[:-1] # remove new line at the end of result.stdout
    
    def _extract_test_line(self, work_dir, project, bug_id):
        command = ['bash', f'{self.shell_scripts_folder}/extract_test_line.sh', f"{project}", f"{bug_id}", f"{work_dir}", f"{self.d4j_path}"]
        result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        assert result.returncode == 0
        if len(result.stdout) < 2:
            return ""
        return result.stdout[:-1] # remove new line at the end of result.stdout

    def _extract_buggy_line(self, work_dir, project, bug_id):
        command = ['bash', f'{self.shell_scripts_folder}/extract_buggy_line.sh', f"{project}", f"{bug_id}", f"{work_dir}", f"{self.d4j_path}"]
        result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        assert result.returncode == 0 
        if len(result.stdout) < 2:
            return ""
        return result.stdout[:-1]

    def _extract_fixed_line(self, work_dir, project, bug_id):
        command = ['bash', f'{self.shell_scripts_folder}/extract_fixed_line.sh', f"{project}", f"{bug_id}", f"{work_dir}", f"{self.d4j_path}"]
        result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        assert result.returncode == 0
        if len(result.stdout) < 2:
            return ""
        return result.stdout[:-1]
    
    def _extract_masked_code(self, work_dir, project, bug_id):
        command = ['bash', f'{self.shell_scripts_folder}/extract_masked_code.sh', f"{project}", f"{bug_id}", f"{work_dir}", f"{self.d4j_path}"]
        result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        assert result.returncode == 0 and len(result.stdout) > 1
        return result.stdout[:-1]
    
    def _extract_code(self, work_dir, project, bug_id):
        command = ['bash', f'{self.shell_scripts_folder}/extract_code.sh', f"{project}", f"{bug_id}", f"{work_dir}", f"{self.d4j_path}"]
        result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        assert result.returncode == 0 and len(result.stdout) > 1
        return result.stdout[:-1]
