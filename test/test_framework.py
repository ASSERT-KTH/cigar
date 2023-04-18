import unittest
from pathlib import Path
from src.framework import Framework

class TestFramework(unittest.TestCase):

    def test_validate_patch_gson_15(self):
        framework = Framework(test_framework="defects4j",
                              cache_folder=Path(__file__).parent.parent / 'data' / 'validate_patch_cache')

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
                              cache_folder=Path(__file__).parent.parent / 'data' / 'validate_patch_cache')

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