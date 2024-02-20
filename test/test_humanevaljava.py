import unittest
from pathlib import Path
from src.framework import Framework
from user_params import UserParams as user_params

class TestHumanEvalJavaFramework(unittest.TestCase):

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.humaneval_path = user_params.HUMANEVAL_PATH
        self.java_home = user_params.JAVA_HOME
        self.tmp_dir = user_params.TMP_DIR

    def test_get_bug_type_ADD(self):
        framework = Framework(name="humanevaljava", list_of_bugs=None,
                              d4j_path=self.humaneval_path, java_home=self.java_home, tmp_dir=self.tmp_dir)

        bug = framework.get_bug_details("humaneval", "ADD")
        
        self.assertEqual(bug.bug_type, "SL SH SF")

    def test_get_bug_type_ADD_ELEMENTS(self):
        framework = Framework(name="humanevaljava", list_of_bugs=None,
                              d4j_path=self.humaneval_path, java_home=self.java_home, tmp_dir=self.tmp_dir)

        bug = framework.get_bug_details("humaneval", "ADD_ELEMENTS")

        self.assertEqual(bug.bug_type, "SH SF")

    def test_get_buggy_lines_ADD(self):
        framework = Framework(name="humanevaljava", list_of_bugs=None,
                              d4j_path=self.humaneval_path, java_home=self.java_home, tmp_dir=self.tmp_dir)

        bug = framework.get_bug_details("humaneval", "ADD")

        self.assertEqual(bug.buggy_lines.strip(), "return x | y;")      

    def test_get_fixed_lines_ADD(self):
        framework = Framework(name="humanevaljava", list_of_bugs=None,
                              d4j_path=self.humaneval_path, java_home=self.java_home, tmp_dir=self.tmp_dir)

        bug = framework.get_bug_details("humaneval", "ADD")

        self.assertEqual(bug.fixed_lines.strip(), "return x + y;")      

    def test_get_test_line_ADD(self):
        framework = Framework(name="humanevaljava", list_of_bugs=None,
                              d4j_path=self.humaneval_path, java_home=self.java_home, tmp_dir=self.tmp_dir)

        bug = framework.get_bug_details("humaneval", "ADD")

        self.assertEqual(bug.test_line.strip(), "org.junit.Assert.assertEquals(")

    def test_get_test_error_message_ADD(self):
        framework = Framework(name="humanevaljava", list_of_bugs=None,
                                d4j_path=self.humaneval_path, java_home=self.java_home, tmp_dir=self.tmp_dir)
        
        bug = framework.get_bug_details("humaneval", "ADD")

        self.assertEqual(bug.test_error_message.strip(), "TEST_ADD.test_2:23 expected:<3> but was:<5>")

    def test_get_test_suite_ADD(self):
        framework = Framework(name="humanevaljava", list_of_bugs=None,
                                d4j_path=self.humaneval_path, java_home=self.java_home, tmp_dir=self.tmp_dir)
        
        bug = framework.get_bug_details("humaneval", "ADD")

        self.assertEqual(bug.test_suite.strip(), "TEST_ADD")

    def test_get_test_name_ADD(self):
        framework = Framework(name="humanevaljava", list_of_bugs=None,
                                d4j_path=self.humaneval_path, java_home=self.java_home, tmp_dir=self.tmp_dir)
        
        bug = framework.get_bug_details("humaneval", "ADD")

        self.assertEqual(bug.test_name.strip(), "test_2")

    def test_get_code_ADD(self):
        framework = Framework(name="humanevaljava", list_of_bugs=None,
                                d4j_path=self.humaneval_path, java_home=self.java_home, tmp_dir=self.tmp_dir)
        
        bug = framework.get_bug_details("humaneval", "ADD")

        self.assertEqual(bug.code.strip(), "public static int add(int x, int y) {\n        return x | y;\n    }")

    def test_get_masked_code_ADD(self):
        framework = Framework(name="humanevaljava", list_of_bugs=None,
                                d4j_path=self.humaneval_path, java_home=self.java_home, tmp_dir=self.tmp_dir)
        
        bug = framework.get_bug_details("humaneval", "ADD")

        self.assertEqual(bug.masked_code.strip(), "public static int add(int x, int y) {\n>>> [ INFILL ] <<<\n    }")

    def test_validate_patch_pass_ADD(self):
        framework = Framework(name="humanevaljava", list_of_bugs=None,
                              d4j_path=self.humaneval_path, java_home=self.java_home, tmp_dir=self.tmp_dir)

        bug = framework.get_bug_details("humaneval", "ADD")

        proposed_patch = "    public static int add(int x, int y) {\n        return x + y;\n    }"

        test_result, test_reason, patch_diff = framework.validate_patch(bug, proposed_patch, mode="SF")
        self.assertEqual(test_result, "PASS")

    def test_validate_patch_fail_ADD(self):
        framework = Framework(name="humanevaljava", list_of_bugs=None,
                              d4j_path=self.humaneval_path, java_home=self.java_home, tmp_dir=self.tmp_dir)

        bug = framework.get_bug_details("humaneval", "ADD")

        proposed_patch = "    public static int add(int x, int y) {\n        return x - y;\n    }"

        test_result, test_reason, patch_diff = framework.validate_patch(bug, proposed_patch, mode="SF")
        self.assertEqual(test_result, "FAIL")

    def test_validate_patch_error_ADD(self):
        framework = Framework(name="humanevaljava", list_of_bugs=None,
                              d4j_path=self.humaneval_path, java_home=self.java_home, tmp_dir=self.tmp_dir)

        bug = framework.get_bug_details("humaneval", "ADD")

        proposed_patch = "    public static int add(int x, int y) {\n        return x ; y;\n    }"

        test_result, test_reason, patch_diff = framework.validate_patch(bug, proposed_patch, mode="SF")
        self.assertEqual(test_result, "ERROR")
        self.assertTrue("not a statement" in test_reason)

    def test_n_shot_examples(self):
        framework = Framework(name="humanevaljava", list_of_bugs=[("humaneval", ["ADD", "X_OR_Y"])],
                              d4j_path=self.humaneval_path, java_home=self.java_home, tmp_dir=self.tmp_dir)
        
        bug = framework.get_bug_details("humaneval", "ADD")

        expected_n_shot_bug_ids = ["X_OR_Y"]

        n_shot_bugs = framework.get_n_shot_bugs(n=1, bug=bug, mode="SF")
        n_shot_bug_ids = [bug.bug_id for bug in n_shot_bugs]

        self.assertEqual(n_shot_bug_ids, expected_n_shot_bug_ids)

    def test_n_shot_examples_excludes_target_bug(self):
        framework = Framework(name="humanevaljava", list_of_bugs=[("humaneval", ["ADD", "X_OR_Y"])],
                              d4j_path=self.humaneval_path, java_home=self.java_home, tmp_dir=self.tmp_dir)
        
        bug = framework.get_bug_details("humaneval", "X_OR_Y")

        expected_n_shot_bug_ids = ["ADD"]

        n_shot_bugs = framework.get_n_shot_bugs(n=1, bug=bug, mode="SF")
        n_shot_bug_ids = [bug.bug_id for bug in n_shot_bugs]

        self.assertEqual(n_shot_bug_ids, expected_n_shot_bug_ids)
