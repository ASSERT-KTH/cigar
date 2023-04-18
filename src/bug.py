
class Bug(object):
    def __init__(self, 
                 test_framework,
                 project,
                 bug_id,
                 file_change_count,
                 line_change_count,
                 masked_buggy_code, 
                 buggy_line, 
                 fixed_line, 
                 test_suite, 
                 test_name, 
                 test_line, 
                 test_error_message):
        self.test_framework = test_framework
        self.project = project
        self.bug_id = bug_id
        self.file_change_count = file_change_count
        self.line_change_count = line_change_count
        self.masked_buggy_code = masked_buggy_code
        self.buggy_line = buggy_line
        self.fixed_line = fixed_line
        self.test_suite = test_suite
        self.test_name = test_name
        self.test_line = test_line
        self.test_error_message = test_error_message
