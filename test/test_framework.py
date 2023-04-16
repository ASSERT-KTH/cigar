import unittest
from src.framework import Framework

class TestFramework(unittest.TestCase):

    def test_validate_patch(self):
        framework = Framework(test_framework="defects4j")
        bug_data = {"project": "Gson", "bug_id": 15}

        framework.reproduce_bug(bug_data)

        code_causes_compilation_error = "    if (Double.isInfini(value)) {"
        code_buggy_fails_test =         "    if (Double.isNaN(value) || Double.isInfinite(value)) {"
        code_fixed_should_pass =        "    if (!lenient && (Double.isNaN(value) || Double.isInfinite(value))) {"

        test_result, _ = framework.validate_patch(bug_data, code_causes_compilation_error)
        self.assertEqual(test_result, "ERROR")

        test_result, _ = framework.validate_patch(bug_data, code_buggy_fails_test)
        self.assertEqual(test_result, "FAIL")

        test_result, _ = framework.validate_patch(bug_data, code_fixed_should_pass)
        self.assertEqual(test_result, "PASS")