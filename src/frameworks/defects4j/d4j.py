from pathlib import Path
from subprocess import PIPE, run

class Defects4J(object):
    def __init__(self):
        self.d4j_path = "/Users/davidhidvegi/Desktop/defects4j/framework/bin"
        self.tmp_dir = "/tmp/defects4j"
        self.bug_dataset = [
            # {"project": "Lang", "bug_id": 16}, # Based on paper ChatRepair can fix this bug
            {"project": "Gson", "bug_id": 15}, # Based on paper ChatRepair can fix this bug
        ]
        self.shell_scripts_folder = Path(__file__).parent

    def reproduce_bug(self, bug_data):
        
        project = bug_data["project"]
        bug_id = bug_data["bug_id"]
        work_dir = f"{self.tmp_dir}/{project}-{bug_id}"

        self._reproduce_buggy_folder(work_dir, project, bug_id)

        test_suite = self._extract_test_suite(work_dir, project, bug_id)
        test_name = self._extract_test_name(work_dir, project, bug_id)
        test_error = self._extract_test_error(work_dir, project, bug_id)
        test_line = self._extract_test_line(work_dir, project, bug_id)
        code = self._extract_code(work_dir, project, bug_id)
        buggy_line = self._extract_buggy_line(work_dir, project, bug_id)
        fixed_line = self._extract_fixed_line(work_dir, project, bug_id)
        masked_code = self._extract_masked_code(work_dir, project, bug_id)

        # Return Bug object

    def validate_patch(self, bug_data, proposed_line_fix):

        project = bug_data["project"]
        bug_id = bug_data["bug_id"]
        work_dir = f"{self.tmp_dir}/{project}-{bug_id}"

        command = ['sh', f'{self.shell_scripts_folder}/validate_patch.sh', f"{project}", f"{bug_id}", f"{work_dir}", f"{self.d4j_path}", f"{proposed_line_fix}"]
        result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)

        test_result = None
        result_reason = None
        
        if result.returncode == 1:
            test_result = result.stderr
            test_result = test_result[test_result.find("error: "):]
            test_result = test_result[:test_result.find("\n")]

            test_result, result_reason = "FAIL", "error: cannot find symbol"
        else:
            all_tests_passed = result.stdout.find("Failing tests: 0") != -1

            if all_tests_passed:
                test_result, result_reason = "PASS", "all tests passed"
            else:
                test_result = "FAIL"
                result_reason = self._extract_test_error(work_dir, project, bug_id)
            
        return test_result, result_reason


    def _reproduce_buggy_folder(self, work_dir, project, bug_id):
        command = ['sh', f'{self.shell_scripts_folder}/reproduce_bug.sh', f"{project}", f"{bug_id}", f"{work_dir}", f"{self.d4j_path}"]
        result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        assert result.returncode == 0

    def _extract_test_suite(self, work_dir, project, bug_id):
        command = ['sh', f'{self.shell_scripts_folder}/extract_test_suite.sh', f"{project}", f"{bug_id}", f"{work_dir}", f"{self.d4j_path}"]
        result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        assert result.returncode == 0 and len(result.stdout) > 1
        return result.stdout[:-1] # remove new line at the end of result.stdout
        
    def _extract_test_name(self, work_dir, project, bug_id):
        command = ['sh', f'{self.shell_scripts_folder}/extract_test_name.sh', f"{project}", f"{bug_id}", f"{work_dir}", f"{self.d4j_path}"]
        result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        assert result.returncode == 0 and len(result.stdout) > 1
        return result.stdout[:-1] # remove new line at the end of result.stdout
    
    def _extract_test_error(self, work_dir, project, bug_id):
        command = ['sh', f'{self.shell_scripts_folder}/extract_test_error.sh', f"{project}", f"{bug_id}", f"{work_dir}", f"{self.d4j_path}"]
        result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        assert result.returncode == 0 and len(result.stdout) > 1
        return result.stdout[:-1] # remove new line at the end of result.stdout
    
    def _extract_test_line(self, work_dir, project, bug_id):
        command = ['sh', f'{self.shell_scripts_folder}/extract_test_line.sh', f"{project}", f"{bug_id}", f"{work_dir}", f"{self.d4j_path}"]
        result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        assert result.returncode == 0 and len(result.stdout) > 1
        return result.stdout[:-1] # remove new line at the end of result.stdout

    def _extract_code(self, work_dir, project, bug_id):
        command = ['sh', f'{self.shell_scripts_folder}/extract_code.sh', f"{project}", f"{bug_id}", f"{work_dir}", f"{self.d4j_path}"]
        result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        assert result.returncode == 0 and len(result.stdout) > 1
        return result.stdout[:-1]

    def _extract_buggy_line(self, work_dir, project, bug_id):
        command = ['sh', f'{self.shell_scripts_folder}/extract_buggy_line.sh', f"{project}", f"{bug_id}", f"{work_dir}", f"{self.d4j_path}"]
        result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        assert result.returncode == 0 and len(result.stdout) > 1
        return result.stdout[:-1]

    def _extract_fixed_line(self, work_dir, project, bug_id):
        command = ['sh', f'{self.shell_scripts_folder}/extract_fixed_line.sh', f"{project}", f"{bug_id}", f"{work_dir}", f"{self.d4j_path}"]
        result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        assert result.returncode == 0 and len(result.stdout) > 1
        return result.stdout[:-1]
    
    def _extract_masked_code(self, work_dir, project, bug_id):
        command = ['sh', f'{self.shell_scripts_folder}/extract_masked_code.sh', f"{project}", f"{bug_id}", f"{work_dir}", f"{self.d4j_path}"]
        result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        assert result.returncode == 0 and len(result.stdout) > 1
        return result.stdout[:-1]

d4j = Defects4J()
bug_data = d4j.bug_dataset[0]

code_causes_compilation_error = "    if (Double.isInfinite(value))) {"
code_buggy_fails_test =         "    if (Double.isNaN(value) || Double.isInfinite(value)) {"
code_fixed_should_pass =        "    if (!lenient && (Double.isNaN(value) || Double.isInfinite(value))) {"

patch_code = code_buggy_fails_test

test_result, result_reason = d4j.validate_patch(bug_data, patch_code)
print(test_result)
print(result_reason)