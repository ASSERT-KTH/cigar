
class Bug(object):
    def __init__(self, masked_buggy_code, buggy_line, test_name, test_line, test_error_message, bug_info):
        self.previous_bug_fixes = """The following Java code contains a buggy line that has been replaced with INFILL:
```java
public class Main {
  INFILL
    return x + y;
  }

  public static void main(String[] args) {
    System.out.println(myMethod(5, 3));
  }
}
```

This was the original buggy line which was at the INFILL location:
static int myMethod(int x, y) {

The correct fix is:
static int myMethod(int x, int y) {
"""
        self.masked_buggy_code = masked_buggy_code
        self.buggy_line = buggy_line
        self.test_name = test_name
        self.test_line = test_line
        self.test_error_message = test_error_message
        self.bug_info = bug_info
