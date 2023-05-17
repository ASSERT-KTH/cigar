import hashlib
import json
from pathlib import Path
from subprocess import PIPE, run
from src.bug import Bug

class Framework(object):
    def __init__(self, test_framework, list_of_bugs, validate_patch_cache_folder=None, n_shot_cache_folder=None):
        assert test_framework in ["defects4j", "quixbugs"]
        self.test_framework = test_framework
        self.list_of_bugs = list_of_bugs
        self.validate_patch_cache_folder = validate_patch_cache_folder
        self.n_shot_cache_folder = n_shot_cache_folder

        self.d4j_path = "/Users/davidhidvegi/Desktop/defects4j/framework/bin"
        self.tmp_dir = f"/tmp/{test_framework}"
        self.shell_scripts_folder = Path(__file__).parent.parent / "frameworks"

    def reproduce_bug(self, project, bug_id, run_tests=True):
        work_dir = f"{self.tmp_dir}/{project}-{bug_id}"

        self.run_bash("checkout_bug", work_dir, project, bug_id)
        if run_tests:
            self.run_bash("compile_and_run_tests", work_dir, project, bug_id)

        bug_type = self.run_bash("get_bug_type", work_dir, project, bug_id).stdout
        test_suite, test_name, test_error, test_line, buggy_lines, fixed_lines, code, masked_code, fixed_code = None, None, None, None, None, None, None, None, None
        if bug_type != "OT":
            if run_tests:
                test_suite = self.run_bash("get_test_suite", work_dir, project, bug_id).stdout
                test_name = self.run_bash("get_test_name", work_dir, project, bug_id).stdout
                test_error = self.run_bash("get_test_error", work_dir, project, bug_id).stdout
                test_line = self.run_bash("get_test_line", work_dir, project, bug_id).stdout
            buggy_lines = self.run_bash("get_buggy_lines", work_dir, project, bug_id).stdout
            fixed_lines = self.run_bash("get_fixed_lines", work_dir, project, bug_id).stdout
            code = self.run_bash("get_code", work_dir, project, bug_id).stdout
            masked_code = self.run_bash("get_masked_code", work_dir, project, bug_id).stdout
            fixed_code = self.run_bash("get_fixed_code", work_dir, project, bug_id).stdout

        return Bug(test_suite=test_suite, test_name=test_name, test_line=test_line, test_error_message=test_error,
                   buggy_lines=buggy_lines, fixed_lines=fixed_lines, code=code, masked_code=masked_code, fixed_code=fixed_code,
                   test_framework=self.test_framework, project=project, bug_id=bug_id, bug_type=bug_type)
    
    def get_n_shot_bugs(self, n: int, bug: Bug, mode: str):
        assert mode in ["SL", "SH", "SF"]

        n_shot_list = []

        if self.n_shot_cache_folder is not None:
            cache_file_path = f"{self.n_shot_cache_folder}/{bug.project}_{mode}.json"
            if Path(cache_file_path).is_file():
                with open(cache_file_path, "r") as file:
                    json_to_load = json.load(file)
                    n_shot_list = json_to_load['n_shot_list']

        if len(n_shot_list) == 0:         
            list_of_project_bugs = [bug_list for bug_list in self.list_of_bugs if bug_list[0] == bug.project]

            for bug_id in list_of_project_bugs[0][1]:

                work_dir = f"{self.tmp_dir}/{bug.project}-{bug_id}"
                if not Path(work_dir).is_dir():
                    self.run_bash("checkout_bug", work_dir, bug.project, bug_id)
                bug_type = self.run_bash("get_bug_type", work_dir, bug.project, bug_id).stdout

                if mode in bug_type:
                    code_len = len(self.run_bash("get_code", work_dir, bug.project, bug_id).stdout)

                    n_shot_list.append({"bug_id": bug_id, "code_len": code_len})
            
            n_shot_list = sorted(n_shot_list, key=lambda k: k['code_len'])

            if self.n_shot_cache_folder is not None:
                with open(cache_file_path, "w") as file:
                    json.dump({"n_shot_list": n_shot_list}, file, indent=4, sort_keys=True)

        n_shot_bug_list = [self.reproduce_bug(bug.project, n_shot["bug_id"], run_tests=False) for n_shot in n_shot_list if n_shot["bug_id"] != bug.bug_id]

        return n_shot_bug_list[:n]

    def validate_patch(self, bug: Bug, proposed_patch: str, mode: str):
        assert mode in ["SL", "SH", "SF"]

        test_result = None
        result_reason = None
        patch_hash = hashlib.md5(str(proposed_patch).encode('utf-8')).hexdigest()

        if self.validate_patch_cache_folder is not None:
            cache_file_path = f"{self.validate_patch_cache_folder}/{self.test_framework}_{bug.project}_{bug.bug_id}_{patch_hash}.json"
            if Path(cache_file_path).is_file():
                with open(cache_file_path, "r") as file:
                    json_to_load = json.load(file)
                    test_result = json_to_load['test_result']
                    result_reason = json_to_load['result_reason']

        if test_result is None and result_reason is None:

            project = bug.project
            bug_id = bug.bug_id
            work_dir = f"{self.tmp_dir}/{project}-{bug_id}"

            result = self.run_bash("validate_patch", work_dir, project, bug_id, proposed_patch, mode)
            
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

        if self.validate_patch_cache_folder is not None:
            with open(cache_file_path, "w") as file:
                json.dump({'patch': proposed_patch, 'test_result': test_result, 'result_reason': result_reason}, file,  indent=4, sort_keys=True)
            
        return test_result, result_reason
    
    def run_bash(self, function, work_dir, project, bug_id, extra_arg1=None, extra_arg2=None):
        command = ['bash', f'{self.shell_scripts_folder}/{self.test_framework}.sh', function, f"{project}", f"{bug_id}", f"{work_dir}", f"{self.d4j_path}", f"{extra_arg1}", f"{extra_arg2}"]
        result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        result.stdout = result.stdout[:-1]
        return result
