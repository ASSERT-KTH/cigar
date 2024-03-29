import unittest
from pathlib import Path
from src.framework import Framework
from user_params import UserParams as user_params

class TestFramework(unittest.TestCase):

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.d4j_path = user_params.D4J_PATH
        self.java_home = user_params.JAVA_HOME
        self.tmp_dir = user_params.TMP_DIR

    def test_get_bug_type_time_6(self):
        framework = Framework(name="defects4j", list_of_bugs=None,
                              d4j_path=self.d4j_path, java_home=self.java_home, tmp_dir=self.tmp_dir)

        bug_time_6 = framework.get_bug_details("Time", 6) # Caused a bug because git show --no-prefix was too small
        
        self.assertEqual(bug_time_6.bug_type, "OT")

    def test_get_bug_type_mockito_5(self):
        framework = Framework(name="defects4j", list_of_bugs=None,
                              d4j_path=self.d4j_path, java_home=self.java_home, tmp_dir=self.tmp_dir)

        project = "Mockito"
        bug_id = "5"

        framework.run_bash("checkout_bug", project, bug_id)

        bug_mockito_5_bug_type = framework.run_bash("get_bug_type", project, bug_id).stdout
        
        self.assertEqual(bug_mockito_5_bug_type, "SL SH SF")

    def test_get_buggy_lines(self):
        framework = Framework(name="defects4j", list_of_bugs=None,
                              d4j_path=self.d4j_path, java_home=self.java_home, tmp_dir=self.tmp_dir)

        bug_time_58 = framework.get_bug_details("Lang", 58) # Edge case, multiple buggy lines

        expected_buggy_lines = """                        && isDigits(numeric.substring(1))
                        && (numeric.charAt(0) == '-' || Character.isDigit(numeric.charAt(0)))) {"""
        
        self.assertEqual(bug_time_58.buggy_lines, expected_buggy_lines)

    def test_get_fixed_lines(self):
        framework = Framework(name="defects4j", list_of_bugs=None,
                              d4j_path=self.d4j_path, java_home=self.java_home, tmp_dir=self.tmp_dir)

        bug_time_54 = framework.get_bug_details("Lang", 54) # Edge case, multiple fixed lines

        expected_fixed_lines = """            if (ch3 == '_') {
                return new Locale(str.substring(0, 2), "", str.substring(4));
            }"""
        
        self.assertEqual(bug_time_54.fixed_lines, expected_fixed_lines)

    def test_get_test_line_time_22(self):
        framework = Framework(name="defects4j", list_of_bugs=None,
                              d4j_path=self.d4j_path, java_home=self.java_home, tmp_dir=self.tmp_dir)

        bug_time_22 = framework.get_bug_details("Time", 22) # Edge case, has multiple test files with same name

        expected_test_line = """            assertEquals(0, test.getWeeks());"""
        
        self.assertEqual(bug_time_22.test_line, expected_test_line)

    def test_get_test_line_math_34(self):
        framework = Framework(name="defects4j", list_of_bugs=None,
                              d4j_path=self.d4j_path, java_home=self.java_home, tmp_dir=self.tmp_dir)

        bug_math_34 = framework.get_bug_details("Math", 34) # Contained a bug, test_line was never found

        expected_test_line = "" # Test line cannot be found
        
        self.assertEqual(bug_math_34.test_line, expected_test_line)

    def test_get_code(self):
        framework = Framework(name="defects4j", list_of_bugs=None,
                              d4j_path=self.d4j_path, java_home=self.java_home, tmp_dir=self.tmp_dir)
        
        bug_time_4 = framework.get_bug_details("Time", 4) # Edge case containing keywords in comments
        bug_time_24 = framework.get_bug_details("Time", 24) # Edge case, selects 2 functions

        self.assertGreater(len(bug_time_4.code), 0)
        self.assertGreater(len(bug_time_24.code), 0)
        self.assertEqual(bug_time_24.code.count("public") + bug_time_24.code.count("private"), 1)

    def test_get_masked_code(self):
        framework = Framework(name="defects4j", list_of_bugs=None,
                              d4j_path=self.d4j_path, java_home=self.java_home, tmp_dir=self.tmp_dir)
        
        bug_chart_10 = framework.get_bug_details("Chart", 10) # SH Bug, 2 line addition, 2 line deletion

        expected_masked_code = '''    public String generateToolTipFragment(String toolTipText) {
>>> [ INFILL ] <<<
            + "\\" alt=\\"\\"";
    }'''

        self.assertEqual(bug_chart_10.masked_code, expected_masked_code)

    def test_validate_patch_gson_15(self):
        framework = Framework(name="defects4j", list_of_bugs=None,
                              d4j_path=self.d4j_path, java_home=self.java_home, tmp_dir=self.tmp_dir)

        bug = framework.get_bug_details("Gson", 15)
        mode = "SL"

        code_causes_compilation_error = "    if (Double.isInfini(value)) {"
        code_buggy_fails_test =         "    if (Double.isNaN(value) || Double.isInfinite(value)) {"
        code_fixed_should_pass =        "    if (!lenient && (Double.isNaN(value) || Double.isInfinite(value))) {"

        test_result, _, _ = framework.validate_patch(bug, code_causes_compilation_error, mode)
        self.assertEqual(test_result, "ERROR")

        test_result, _, _ = framework.validate_patch(bug, code_buggy_fails_test, mode)
        self.assertEqual(test_result, "FAIL")

        test_result, _, _ = framework.validate_patch(bug, code_fixed_should_pass, mode)
        self.assertEqual(test_result, "PASS")

    def test_validate_patch_chart_10(self):
        framework = Framework(name="defects4j", list_of_bugs=None,
                              d4j_path=self.d4j_path, java_home=self.java_home, tmp_dir=self.tmp_dir)

        bug = framework.get_bug_details("Closure", 10) # Single Function Bug (fixed by the authors)

        test_result, _, _ = framework.validate_patch(bug, bug.fixed_lines, mode="SL")
        self.assertEqual(test_result, "PASS")

    def test_validate_patch_closure_10(self):
        framework = Framework(name="defects4j", list_of_bugs=None,
                              d4j_path=self.d4j_path, java_home=self.java_home, tmp_dir=self.tmp_dir)

        bug = framework.get_bug_details("Chart", 10) # Single Function Bug, solution contains escape characters

        sf_patch_fix = bug.fixed_code

        test_result, _, _ = framework.validate_patch(bug, sf_patch_fix, mode="SF")
        self.assertEqual(test_result, "PASS")

    def test_validate_patch_lang_16(self):
        framework = Framework(name="defects4j", list_of_bugs=None,
                              d4j_path=self.d4j_path, java_home=self.java_home, tmp_dir=self.tmp_dir)

        bug = framework.get_bug_details("Lang", 16)
        mode = "SL"

        code_causes_compilation_error = '        if (str.startsWith("0x") || str.startsWith("-0x")))))) {'
        code_buggy_fails_test =         '        if (str.startsWith("0x") || str.startsWith("-0x")) {'
        code_fixed_should_pass =        '        if (str.startsWith("0x") || str.startsWith("-0x") || str.startsWith("0X") || str.startsWith("-0X")) {'
        code_fixed_should_pass_2 =      '        if (str.regionMatches(true, 0, \"0x\", 0, 2) || str.regionMatches(true, 0, \"-0x\", 0, 3)) {'

        test_result, _, _ = framework.validate_patch(bug, code_causes_compilation_error, mode)
        self.assertEqual(test_result, "ERROR")

        test_result, _, _ = framework.validate_patch(bug, code_buggy_fails_test, mode)
        self.assertEqual(test_result, "FAIL")

        test_result, _, _ = framework.validate_patch(bug, code_fixed_should_pass, mode)
        self.assertEqual(test_result, "PASS")

        test_result, _, _ = framework.validate_patch(bug, code_fixed_should_pass_2, mode)
        self.assertEqual(test_result, "PASS")

    def test_validate_patch_lang_54(self):
        framework = Framework(name="defects4j", list_of_bugs=None,
                              d4j_path=self.d4j_path, java_home=self.java_home, tmp_dir=self.tmp_dir)

        bug = framework.get_bug_details("Lang", 54) # Single Hunk Bug

        code_fixed_should_pass = """            if (ch3 == '_') {
                return new Locale(str.substring(0, 2), "", str.substring(4));
            }"""

        test_result, _, _ = framework.validate_patch(bug, code_fixed_should_pass, mode="SH")
        self.assertEqual(test_result, "PASS")

    def test_validate_patch_math_10(self):
        framework = Framework(name="defects4j", list_of_bugs=None,
                              d4j_path=self.d4j_path, java_home=self.java_home, tmp_dir=self.tmp_dir)

        bug = framework.get_bug_details("Math", 10) # Single Function Bug (fixed by the authors)

        test_result, _, _ = framework.validate_patch(bug, bug.fixed_lines, mode="SL")
        self.assertEqual(test_result, "PASS")

    def test_validate_patch_mockito_24(self):
        framework = Framework(name="defects4j", list_of_bugs=None,
                              d4j_path=self.d4j_path, java_home=self.java_home, tmp_dir=self.tmp_dir)

        mode = "SL"
        bug = framework.get_bug_details("Mockito", 24)

        test_result, _, _ = framework.validate_patch(bug, bug.fixed_lines, mode)
        self.assertEqual(test_result, "PASS")

    def test_validate_patch_time_18(self):
        framework = Framework(name="defects4j", list_of_bugs=None,
                              d4j_path=self.d4j_path, java_home=self.java_home, tmp_dir=self.tmp_dir)

        mode = "SF"
        bug = framework.get_bug_details("Time", 18)

        original_buggy_code = '''    public long getDateTimeMillis(int year, int monthOfYear, int dayOfMonth,
                                  int hourOfDay, int minuteOfHour,
                                  int secondOfMinute, int millisOfSecond)
        throws IllegalArgumentException
    {
        Chronology base;
        if ((base = getBase()) != null) {
            return base.getDateTimeMillis
                (year, monthOfYear, dayOfMonth,
                 hourOfDay, minuteOfHour, secondOfMinute, millisOfSecond);
        }

        // Assume date is Gregorian.
        long instant;
            instant = iGregorianChronology.getDateTimeMillis
                (year, monthOfYear, dayOfMonth,
                 hourOfDay, minuteOfHour, secondOfMinute, millisOfSecond);
        if (instant < iCutoverMillis) {
            // Maybe it's Julian.
            instant = iJulianChronology.getDateTimeMillis
                (year, monthOfYear, dayOfMonth,
                 hourOfDay, minuteOfHour, secondOfMinute, millisOfSecond);
            if (instant >= iCutoverMillis) {
                // Okay, it's in the illegal cutover gap.
                throw new IllegalArgumentException("Specified date does not exist");
            }
        }
        return instant;
    }'''
        proposed_buggy_code = '''    public long getDateTimeMillis(int year, int monthOfYear, int dayOfMonth,
                                  int hourOfDay, int minuteOfHour,
                                  int secondOfMinute, int millisOfSecond)
        throws IllegalArgumentException
    {
        Chronology base;
        if ((base = getBase()) != null) {
            return base.getDateTimeMillis
                (year, monthOfYear, dayOfMonth,
                 hourOfDay, minuteOfHour, secondOfMinute, millisOfSecond);
        }

        // Assume date is Gregorian.
        long instant;
        if (year > 1582 || year == 1582 && (monthOfYear > 10 || monthOfYear == 10 && dayOfMonth >= 15)) {
            instant = iGregorianChronology.getDateTimeMillis
                (year, monthOfYear, dayOfMonth,
                 hourOfDay, minuteOfHour, secondOfMinute, millisOfSecond);
            if (instant < iCutoverMillis) {
                // Maybe it's Julian.
                instant = iJulianChronology.getDateTimeMillis
                    (year, monthOfYear, dayOfMonth,
                     hourOfDay, minuteOfHour, secondOfMinute, millisOfSecond);
                if (instant >= iCutoverMillis) {
                    // Okay, it's in the illegal cutover gap.
                    throw new IllegalArgumentException("Specified date does not exist");
                }
            }
        } else {
            // Maybe it's Julian.
            instant = iJulianChronology.getDateTimeMillis
                (year, monthOfYear, dayOfMonth,
                 hourOfDay, minuteOfHour, secondOfMinute, millisOfSecond);
            if (instant < iCutoverMillis) {
                // Okay, it's after the Gregorian cut-over but before the
                // start of the Julian calendar.  Drop through.
                throw new IllegalArgumentException("Specified date does not exist");
            }
        }
        return instant;
    }'''

        test_result, _, _ = framework.validate_patch(bug, original_buggy_code, mode)
        self.assertEqual(test_result, "FAIL")

        test_result, _, _ = framework.validate_patch(bug, proposed_buggy_code, mode)
        self.assertEqual(test_result, "FAIL")

    def test_validate_patch_time_16_compilation_error_reason(self):
        framework = Framework(name="defects4j", list_of_bugs=None,
                              d4j_path=self.d4j_path, java_home=self.java_home, tmp_dir=self.tmp_dir)

        bug = framework.get_bug_details("Time", 16) # Single Function Bug, Compilation Error doesn't contain 'error' in stderr

        buggy_function_code = '''    public int parseInto(ReadWritableInstant instant, String text, int position) {
        DateTimeParser parser = requireParser();
        if (instant == null) {
            throw new IllegalArgumentException("Instant must not be null");
        }

        long instantMillis = instant.getMillis();
        Chronology chrono = instant.getChronology();
        chrono = selectChronology(chrono);
        DateTimeParserBucket bucket = new DateTimeParserBucket(
            instantMillis, chrono, iLocale, iPivotYear, iDefaultYear);
        int newPos = parser.parseInto(bucket, text, position);
        if (bucket.computeMillis(false, text) <= instantMillis) {
            newPos = ~position;
        } else {
            instant.setMillis(bucket.computeMillis(false, text));
            if (iOffsetParsed && bucket.getOffsetInteger() != null) {
                int parsedOffset = bucket.getOffsetInteger();
                DateTimeZone parsedZone = DateTimeZone.forOffsetMillis(parsedOffset);
                chrono = chrono.withZone(parsedZone);
            } else if (bucket.getZone() != null) {
                chrono = chrono.withZone(bucket.getZone());
            }
            instant.setChronology(chrono);
            if (iZone != null) {
                instant.setZone(iZone);
            }
        }
        return newPos;
    }'''
        expected_test_reason = " java.lang.IllegalArgumentException: 0"

        test_result, test_reason, _ = framework.validate_patch(bug, buggy_function_code, mode="SF")
        self.assertEqual(test_result, "ERROR")
        self.assertEqual(test_reason, expected_test_reason)

    def test_validate_patch_timeout_lang_22(self):
        framework = Framework(name="defects4j", list_of_bugs=None,
                              d4j_path=self.d4j_path, java_home=self.java_home, tmp_dir=self.tmp_dir)

        bug = framework.get_bug_details("Lang", 22) # Single Function Bug, ChatGPT proposed a patch that has infinite while loop

        proposed_patch = '''private static int greatestCommonDivisor(int a, int b) {
    if (Math.abs(a) <= 1 || Math.abs(b) <= 1) { // either operand is abs 1, return 1
        return 1;
    }
    int gcd = 1;
    if (a == 0 || b == 0) { // if one operand is 0, return the other
        return Math.abs(a) + Math.abs(b);
    }
    // keep a and b negative, as negative integers range down to
    // -2^31, while positive numbers can only be as large as 2^31-1
    if (a > 0) {
        a = -a;
    }
    if (b > 0) {
        b = -b;
    }

    // extract common factors of 2
    int k = 0;
    while ((a & 1) == 0 && (b & 1) == 0) {
        a /= 2;
        b /= 2;
        k++;
    }

    // reduce a and b
    while (a != 0 && b != 0) {
        while ((a & 1) == 0) {
            a /= 2;
        }
        while ((b & 1) == 0) {
            b /= 2;
        }
        if (Math.abs(a) >= Math.abs(b)) {
            a = a + b;
        } else {
            b = a + b;
        }
    }
    gcd = (a == 0) ? b : a;

    return gcd * (1 << k); // gcd is gcd * 2^k
}'''

        test_result, test_reason, _ = framework.validate_patch(bug, proposed_patch, mode="SF")
        self.assertEqual(test_result, "ERROR")
        self.assertEqual(test_reason, "Test timed out after 300 seconds")

    def test_n_shot_examples(self):
        framework = Framework(name="defects4j", list_of_bugs=[("Time", [1, 4, 16, 19])],
                              d4j_path=self.d4j_path, java_home=self.java_home, tmp_dir=self.tmp_dir)
        
        bug = framework.get_bug_details("Time", 1)

        expected_n_shot_bug_ids = [16, 19, 4]

        n_shot_bugs = framework.get_n_shot_bugs(n=3, bug=bug, mode="SL")
        n_shot_bug_ids = [bug.bug_id for bug in n_shot_bugs]

        self.assertEqual(n_shot_bug_ids, expected_n_shot_bug_ids)

    def test_n_shot_examples_excludes_target_bug(self):
        framework = Framework(name="defects4j", list_of_bugs=[("Time", [1, 4, 16, 19])],
                              d4j_path=self.d4j_path, java_home=self.java_home, tmp_dir=self.tmp_dir)
        
        bug_id = 16
        project = "Time"
        bug = framework.get_bug_details(project, bug_id)

        expected_n_shot_bug_ids = [19, 4]

        n_shot_bugs = framework.get_n_shot_bugs(n=2, bug=bug, mode="SL")
        n_shot_bug_ids = [b.bug_id for b in n_shot_bugs]

        self.assertEqual(n_shot_bug_ids, expected_n_shot_bug_ids)

    def test_reproduce_bug(self):
        framework = Framework(name="defects4j", list_of_bugs=None,
                              d4j_path=self.d4j_path, java_home=self.java_home, tmp_dir=self.tmp_dir)
        
        bug1 = framework.get_bug_details("Time", 19)
        bug2 = framework.get_bug_details("Time", 5)
