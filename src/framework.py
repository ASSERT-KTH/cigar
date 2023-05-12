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
        self.shell_scripts_folder = Path(__file__).parent.parent / "frameworks"

    def reproduce_bug(self, project, bug_id):
        work_dir = f"{self.tmp_dir}/{project}-{bug_id}"

        self.run_bash("reproduce_bug", work_dir, project, bug_id)

        bug_type = self.run_bash("get_bug_type", work_dir, project, bug_id).stdout
        if bug_type == "OT":
            return None
        
        test_suite = self.run_bash("get_test_suite", work_dir, project, bug_id).stdout
        test_name = self.run_bash("get_test_name", work_dir, project, bug_id).stdout
        test_error = self.run_bash("get_test_error", work_dir, project, bug_id).stdout
        test_line = self.run_bash("get_test_line", work_dir, project, bug_id).stdout
        buggy_line = self.run_bash("get_buggy_line", work_dir, project, bug_id).stdout
        fixed_line = self.run_bash("get_fixed_line", work_dir, project, bug_id).stdout
        code = self.run_bash("get_code", work_dir, project, bug_id).stdout
        masked_code = self.run_bash("get_masked_code", work_dir, project, bug_id).stdout

        return Bug(test_framework=self.test_framework,
                   project=project,
                   bug_id=bug_id,
                   bug_type=bug_type,
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

            result = self.run_bash("validate_patch", work_dir, project, bug_id, proposed_line_fix)
            
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
                    result_reason = self.run_bash("get_test_error", work_dir, project, bug_id).stdout

        if self.cache_folder is not None:
            with open(cache_file_path, "w") as file:
                json.dump({'patch': proposed_line_fix, 'test_result': test_result, 'result_reason': result_reason}, file,  indent=4, sort_keys=True)
            
        return test_result, result_reason
    
    def run_bash(self, function, work_dir, project, bug_id, extra_arg=None):
        command = ['bash', f'{self.shell_scripts_folder}/{self.test_framework}.sh', function, f"{project}", f"{bug_id}", f"{work_dir}", f"{self.d4j_path}", f"{extra_arg}"]
        result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        assert result.returncode == 0
        result.stdout = result.stdout[:-1]
        return result
