import unittest
from pathlib import Path
from src.framework import Framework

class TestFramework(unittest.TestCase):

    def test_get_buggy_lines(self):
        framework = Framework(test_framework="defects4j",
                              list_of_bugs=None)

        bug_time_58 = framework.reproduce_bug("Lang", 58, run_tests=False) # Edge case, multiple buggy lines

        expected_buggy_lines = """                        && isDigits(numeric.substring(1))
                        && (numeric.charAt(0) == '-' || Character.isDigit(numeric.charAt(0)))) {"""
        
        self.assertEqual(bug_time_58.buggy_lines, expected_buggy_lines)

    def test_get_fixed_lines(self):
        framework = Framework(test_framework="defects4j",
                              list_of_bugs=None)

        bug_time_54 = framework.reproduce_bug("Lang", 54, run_tests=False) # Edge case, multiple fixed lines

        expected_fixed_lines = """            if (ch3 == '_') {
                return new Locale(str.substring(0, 2), "", str.substring(4));
            }"""
        
        self.assertEqual(bug_time_54.fixed_lines, expected_fixed_lines)

    def test_get_code(self):
        framework = Framework(test_framework="defects4j",
                              list_of_bugs=None)
        
        bug_time_4 = framework.reproduce_bug("Time", 4, run_tests=False) # Edge case containing keywords in comments
        bug_time_24 = framework.reproduce_bug("Time", 24, run_tests=False) # Edge case, selects 2 functions

        self.assertGreater(len(bug_time_4.code), 0)
        self.assertGreater(len(bug_time_24.code), 0)
        self.assertEqual(bug_time_24.code.count("public") + bug_time_24.code.count("private"), 1)

    def test_get_masked_code(self):
        framework = Framework(test_framework="defects4j",
                              list_of_bugs=None)
        
        bug_chart_10 = framework.reproduce_bug("Chart", 10, run_tests=False) # SH Bug, 2 line addition, 2 line deletion

        expected_masked_code = '''    public String generateToolTipFragment(String toolTipText) {
INFILL
            + "\\" alt=\\"\\"";
    }'''

        self.assertEqual(bug_chart_10.masked_code, expected_masked_code)

    def test_validate_patch_gson_15(self):
        framework = Framework(test_framework="defects4j",
                              list_of_bugs=[("Gson", [15])])

        bug = framework.reproduce_bug("Gson", 15, run_tests=False)
        mode = "SL"

        code_causes_compilation_error = "    if (Double.isInfini(value)) {"
        code_buggy_fails_test =         "    if (Double.isNaN(value) || Double.isInfinite(value)) {"
        code_fixed_should_pass =        "    if (!lenient && (Double.isNaN(value) || Double.isInfinite(value))) {"

        test_result, _ = framework.validate_patch(bug, code_causes_compilation_error, mode)
        self.assertEqual(test_result, "ERROR")

        test_result, _ = framework.validate_patch(bug, code_buggy_fails_test, mode)
        self.assertEqual(test_result, "FAIL")

        test_result, _ = framework.validate_patch(bug, code_fixed_should_pass, mode)
        self.assertEqual(test_result, "PASS")

    def test_validate_patch_lang_16(self):
        framework = Framework(test_framework="defects4j",
                              list_of_bugs=[("Lang", [16])])

        bug = framework.reproduce_bug("Lang", 16, run_tests=False)
        mode = "SL"

        code_causes_compilation_error = '        if (str.startsWith("0x") || str.startsWith("-0x")))))) {'
        code_buggy_fails_test =         '        if (str.startsWith("0x") || str.startsWith("-0x")) {'
        code_fixed_should_pass =        '        if (str.startsWith("0x") || str.startsWith("-0x") || str.startsWith("0X") || str.startsWith("-0X")) {'
        code_fixed_should_pass_2 =      '        if (str.regionMatches(true, 0, \"0x\", 0, 2) || str.regionMatches(true, 0, \"-0x\", 0, 3)) {'

        test_result, _ = framework.validate_patch(bug, code_causes_compilation_error, mode)
        self.assertEqual(test_result, "ERROR")

        test_result, _ = framework.validate_patch(bug, code_buggy_fails_test, mode)
        self.assertEqual(test_result, "FAIL")

        test_result, _ = framework.validate_patch(bug, code_fixed_should_pass, mode)
        self.assertEqual(test_result, "PASS")

        test_result, _ = framework.validate_patch(bug, code_fixed_should_pass_2, mode)
        self.assertEqual(test_result, "PASS")

    def test_validate_patch_lang_54(self):
        framework = Framework(test_framework="defects4j",
                              list_of_bugs=[("Lang", [54])])

        bug = framework.reproduce_bug("Lang", 54, run_tests=False) # Single Hunk Bug

        code_fixed_should_pass = """            if (ch3 == '_') {
                return new Locale(str.substring(0, 2), "", str.substring(4));
            }"""

        test_result, _ = framework.validate_patch(bug, code_fixed_should_pass, mode="SH")
        self.assertEqual(test_result, "PASS")

    def test_validate_patch_chart_10(self):
        framework = Framework(test_framework="defects4j",
                              list_of_bugs=[("Chart", [10])])

        bug = framework.reproduce_bug("Chart", 10, run_tests=False) # Single Function Bug, solution contains escape characters

        sf_patch_fix = bug.masked_code.replace("INFILL", bug.fixed_lines)

        test_result, _ = framework.validate_patch(bug, sf_patch_fix, mode="SF")
        self.assertEqual(test_result, "PASS")

    def test_n_shot_examples(self):
        framework = Framework(test_framework="defects4j",
                              list_of_bugs=[("Time", [1, 4, 16, 19])])
        
        bug = framework.reproduce_bug("Time", 1, run_tests=False)

        expected_n_shot_bug_ids = [16, 19, 4]

        n_shot_bug_id_list = framework.get_n_shot_bug_id_list(n=3, project="Time", mode="SL")

        self.assertEqual(n_shot_bug_id_list, expected_n_shot_bug_ids)

    def test_n_shot_examples_excludes_target_bug(self):
        framework = Framework(test_framework="defects4j",
                              list_of_bugs=[("Time", [1, 4, 16, 19])])
        
        bug_id = 16
        project = "Time"
        bug = framework.reproduce_bug(project, bug_id, run_tests=False)

        expected_n_shot_bug_ids = [19, 4]

        n_shot_bug_id_list = framework.get_n_shot_bug_id_list(n=3, project=project, mode="SL")
        n_shot_bug_id_list.remove(bug_id)

        self.assertEqual(n_shot_bug_id_list, expected_n_shot_bug_ids)
