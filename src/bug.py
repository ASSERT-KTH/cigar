
class Bug(object):
    def __init__(self, 
                 test_framework,
                 project,
                 bug_id,
                 bug_type,
                 code,
                 masked_code, 
                 buggy_lines, 
                 fixed_lines, 
                 test_suite, 
                 test_name, 
                 test_line, 
                 test_error_message):
        self.test_framework = test_framework
        self.project = project
        self.bug_id = bug_id
        self.bug_type = bug_type
        self.code = code
        self.masked_code = masked_code
        self.buggy_lines = buggy_lines
        self.fixed_lines = fixed_lines
        self.test_suite = test_suite
        self.test_name = test_name
        self.test_line = test_line
        self.test_error_message = test_error_message
