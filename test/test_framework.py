import unittest
from pathlib import Path
from src.framework import Framework

class TestFramework(unittest.TestCase):

    def test_get_buggy_lines(self):
        framework = Framework(test_framework="defects4j",
                              list_of_bugs=None)

        bug_time_58 = framework.reproduce_bug("Lang", 58) # Edge case, multiple buggy lines

        expected_buggy_lines = """                        && isDigits(numeric.substring(1))
                        && (numeric.charAt(0) == '-' || Character.isDigit(numeric.charAt(0)))) {"""
        
        self.assertEqual(bug_time_58.buggy_lines, expected_buggy_lines)

    def test_get_fixed_lines(self):
        framework = Framework(test_framework="defects4j",
                              list_of_bugs=None)

        bug_time_54 = framework.reproduce_bug("Lang", 54) # Edge case, multiple fixed lines

        expected_fixed_lines = """            if (ch3 == '_') {
                return new Locale(str.substring(0, 2), "", str.substring(4));
            }"""
        
        self.assertEqual(bug_time_54.fixed_lines, expected_fixed_lines)

    def test_get_code(self):
        framework = Framework(test_framework="defects4j",
                              list_of_bugs=None)
        
        bug_time_4 = framework.reproduce_bug("Time", 4) # Edge case containing keywords in comments
        bug_time_24 = framework.reproduce_bug("Time", 24) # Edge case, selects 2 functions

        self.assertGreater(len(bug_time_4.code), 0)
        self.assertGreater(len(bug_time_24.code), 0)
        self.assertEqual(bug_time_24.code.count("public") + bug_time_24.code.count("private"), 1)

    def test_get_masked_code(self):
        framework = Framework(test_framework="defects4j",
                              list_of_bugs=None)
        
        bug_time_24 = framework.reproduce_bug("Time", 24) # Single Hunk Bug
        bug_lang_58 = framework.reproduce_bug("Lang", 58) # SH Bug, 2 line addition, 2 line deletion

        self.assertEqual(bug_time_24.masked_code.count("INFILL"), 1)
        self.assertEqual(bug_lang_58.masked_code.count("INFILL"), 1)

    def test_validate_patch_gson_15(self):
        framework = Framework(test_framework="defects4j",
                              list_of_bugs=[("Gson", [15])])

        bug = framework.reproduce_bug("Gson", 15)

        code_causes_compilation_error = "    if (Double.isInfini(value)) {"
        code_buggy_fails_test =         "    if (Double.isNaN(value) || Double.isInfinite(value)) {"
        code_fixed_should_pass =        "    if (!lenient && (Double.isNaN(value) || Double.isInfinite(value))) {"

        test_result, _ = framework.validate_patch(bug, code_causes_compilation_error)
        self.assertEqual(test_result, "ERROR")

        test_result, _ = framework.validate_patch(bug, code_buggy_fails_test)
        self.assertEqual(test_result, "FAIL")

        test_result, _ = framework.validate_patch(bug, code_fixed_should_pass)
        self.assertEqual(test_result, "PASS")

    def test_validate_patch_lang_16(self):
        framework = Framework(test_framework="defects4j",
                              list_of_bugs=[("Lang", [16])])

        bug = framework.reproduce_bug("Lang", 16)

        code_causes_compilation_error = '        if (str.startsWith("0x") || str.startsWith("-0x")))))) {'
        code_buggy_fails_test =         '        if (str.startsWith("0x") || str.startsWith("-0x")) {'
        code_fixed_should_pass =        '        if (str.startsWith("0x") || str.startsWith("-0x") || str.startsWith("0X") || str.startsWith("-0X")) {'
        code_fixed_should_pass_2 =       '        if (str.regionMatches(true, 0, \"0x\", 0, 2) || str.regionMatches(true, 0, \"-0x\", 0, 3)) {'

        test_result, _ = framework.validate_patch(bug, code_causes_compilation_error)
        self.assertEqual(test_result, "ERROR")

        test_result, _ = framework.validate_patch(bug, code_buggy_fails_test)
        self.assertEqual(test_result, "FAIL")

        test_result, _ = framework.validate_patch(bug, code_fixed_should_pass)
        self.assertEqual(test_result, "PASS")

        test_result, _ = framework.validate_patch(bug, code_fixed_should_pass_2)
        self.assertEqual(test_result, "PASS")

    def test_n_shot_examples(self):
        framework = Framework(test_framework="defects4j",
                              list_of_bugs=[("Time", [i for i in range(1, 28) if i != 21])])
        
        bug = framework.reproduce_bug("Time", 4)

        expected_n_shot_bug_ids = [16, 19, 4]

        n_shot_examples = framework.get_n_shot_bugs(n=3, bug=bug, mode="SL")
        n_shot_bug_ids = [bug.bug_id for bug in n_shot_examples]

        self.assertEqual(n_shot_bug_ids, expected_n_shot_bug_ids)
