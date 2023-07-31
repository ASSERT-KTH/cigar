import hashlib
import json
import logging
from pathlib import Path
from subprocess import PIPE, run
from src.bug import Bug
from prog_params import ProgParams as prog_params

class Framework(object):
    def __init__(self, name, list_of_bugs, d4j_path, java_home, tmp_dir, 
                 bug_details_cache_folder=None, validate_patch_cache_folder=None, n_shot_cache_folder=None):
        assert name in ["defects4j", "human_eval_java"]
        self.name = name
        self.list_of_bugs = list_of_bugs
        self.validate_patch_cache_folder = validate_patch_cache_folder
        self.n_shot_cache_folder = n_shot_cache_folder
        self.d4j_path = d4j_path
        self.java_home = java_home
        self.tmp_dir = tmp_dir
        self.bug_details_cache_folder = bug_details_cache_folder

        self.shell_script_folder = prog_params.shell_script_folder

    def get_bug_details(self, project, bug_id):
        if self.bug_details_cache_folder is not None:
            file_path = f"{self.bug_details_cache_folder}/{project}-{bug_id}.json"
            if Path(file_path).is_file():
                logging.debug(f"Retrieving bug details from cache (project={project}, bug_id={bug_id})")
                with open(file_path, "r") as f:
                    bug_details = json.load(f)
                return Bug(**bug_details)

        logging.debug(f"Checking out bug (project={project}, bug_id={bug_id}))")
        self.run_bash("checkout_bug", project, bug_id)

        bug_type = self.run_bash("get_bug_type", project, bug_id).stdout
        test_suite, test_name, test_error, test_line, buggy_lines, fixed_lines, code, masked_code, fixed_code = None, None, None, None, None, None, None, None, None
        if bug_type != "OT":
            logging.debug(f"Compiling and running tests")
            self.run_bash("compile_and_run_tests", project, bug_id)
            logging.debug(f"Retreiving test suite")
            test_suite = self.run_bash("get_test_suite", project, bug_id).stdout
            logging.debug(f"Retreiving test name")
            test_name = self.run_bash("get_test_name", project, bug_id).stdout
            logging.debug(f"Retreiving test error message")
            test_error = self.run_bash("get_test_error", project, bug_id).stdout
            logging.debug(f"Retreiving test line")
            test_line = self.run_bash("get_test_line", project, bug_id).stdout
            logging.debug(f"Retreiving buggy lines")
            buggy_lines = self.run_bash("get_buggy_lines", project, bug_id).stdout
            logging.debug(f"Retreiving fixed lines")
            fixed_lines = self.run_bash("get_fixed_lines", project, bug_id).stdout
            logging.debug(f"Retreiving code")
            code = self.run_bash("get_code", project, bug_id).stdout
            logging.debug(f"Retreiving masked code")
            masked_code = self.run_bash("get_masked_code", project, bug_id).stdout
            logging.debug(f"Retreiving fixed code")
            fixed_code = self.run_bash("get_fixed_code", project, bug_id).stdout

        bug = Bug(test_suite=test_suite, test_name=test_name, test_line=test_line, test_error_message=test_error,
                  buggy_lines=buggy_lines, fixed_lines=fixed_lines, code=code, masked_code=masked_code, fixed_code=fixed_code,
                  test_framework=self.name, project=project, bug_id=bug_id, bug_type=bug_type)

        if self.bug_details_cache_folder is not None:
            with open(f'{file_path}', 'w') as f:
                vars_object = vars(bug)
                f.write(json.dumps(vars_object, indent=4, sort_keys=True))

        return bug
    
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
                n_shot_bug = self.get_bug_details(bug.project, bug_id)

                if mode in n_shot_bug.bug_type:
                    code_len = len(n_shot_bug.code)
                    if code_len > 0:
                        n_shot_list.append({"bug_id": bug_id, "code_len": code_len})
            
            n_shot_list = sorted(n_shot_list, key=lambda k: k['code_len'])

            if self.n_shot_cache_folder is not None:
                with open(cache_file_path, "w") as file:
                    json.dump({"n_shot_list": n_shot_list}, file, indent=4, sort_keys=True)

        n_shot_bug_id_list = [n_shot["bug_id"] for n_shot in n_shot_list if n_shot["bug_id"] != bug.bug_id]
        n = min(n, len(n_shot_bug_id_list))
        n_shot_bug_id_list = n_shot_bug_id_list[:n]
        n_shot_bug_list = [self.get_bug_details(bug.project, bug_id) for bug_id in n_shot_bug_id_list]

        return n_shot_bug_list

    def validate_patch(self, bug: Bug, proposed_patch: str, mode: str):
        assert mode in ["SL", "SH", "SF"]

        test_result = None
        result_reason = None
        patch_hash = hashlib.md5(str(proposed_patch).encode('utf-8')).hexdigest()

        if self.validate_patch_cache_folder is not None:
            cache_file_path = f"{self.validate_patch_cache_folder}/{self.name}_{bug.project}_{bug.bug_id}_{mode}_{patch_hash}.json"
            if Path(cache_file_path).is_file():
                with open(cache_file_path, "r") as file:
                    json_to_load = json.load(file)
                    test_result = json_to_load['test_result']
                    result_reason = json_to_load['result_reason']
                    patch_diff = json_to_load['patch_diff']
                logging.info(f"Retrieved test result from cache: {patch_hash}")

        if test_result is None and result_reason is None:

            project = bug.project
            bug_id = bug.bug_id
            
            self.run_bash("checkout_bug", bug.project, bug.bug_id)

            result = self.run_bash("validate_patch", project, bug_id, proposed_patch, mode)
            patch_diff = self.run_bash("get_patch_git_diff", bug.project, bug.bug_id).stdout
            
            if result.returncode != 0:
                if result.stderr.find("error: ") > 0:
                    result_reason = result.stderr
                    result_reason = result_reason[result_reason.find("error: "):]
                    result_reason = result_reason[:result_reason.find("\n")]
                elif "BUILD FAILED" in result.stderr:
                    stderr_lines = result.stderr.split("\n")
                    build_failed_line_i = next((i for i, line in enumerate(stderr_lines) if "BUILD FAILED" in line), None) # line number of line that contains "BUILD FAILED"
                    result_reason = stderr_lines[build_failed_line_i+1]
                    result_reason = result_reason[result_reason.find(' '):]
                else:
                    result_reason = "Test timed out after 600 seconds"

                test_result, result_reason = "ERROR", result_reason # compilation error
            else:
                all_tests_passed = result.stdout.find("Failing tests: 0") != -1

                if all_tests_passed:
                    test_result, result_reason = "PASS", "all tests passed" # test pass
                else:
                    test_result = "FAIL" # test fail
                    result_reason = self.run_bash("get_test_error", project, bug_id).stdout

            if self.validate_patch_cache_folder is not None:
                with open(cache_file_path, "w") as file:
                    json.dump({'patch': proposed_patch, 'test_result': test_result, 'result_reason': result_reason, 'patch_diff': patch_diff}, file,  indent=4, sort_keys=True)
            
        return test_result, result_reason, patch_diff
    
    def run_bash(self, function, project, bug_id, extra_arg1=None, extra_arg2=None):
        work_dir = f"{self.tmp_dir}/{project}-{bug_id}"
        command = ['bash', f'{self.shell_script_folder}/{self.name}.sh', function, f"{project}", f"{bug_id}", f"{work_dir}", f"{self.java_home}", f"{self.d4j_path}", f"{extra_arg1}", f"{extra_arg2}"]
        result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        if len(result.stdout) > 0:
            if result.stdout[-1] == "\n":
                result.stdout = result.stdout[:-1]
        return result
