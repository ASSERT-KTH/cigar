
class Bug(object):
    def __init__(self):
        self.previous_bug_fixes = """The following Java code contains a buggy line that has been replaced with INFILL:
```java
public class Main {
  public static void main(String[] args) {
    INFILL
  }
}
```

This was the original buggy line which was at the INFILL location:
System.println("Hello World");

The correct fix is:
System.out.println("Hello World");

The following Java code contains a buggy line that has been replaced with INFILL:
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
        self.masked_buggy_code = """JSType result = builder.build();
INFILL
    return result;
} else if (this.isObject() && that.isObject()) {
"""
        self.buggy_line = """if (result != null) {"""
        self.test_name = "testGreatestSubtypeUnionTypes5()"
        self.test_line = """assertEquals("NO_OBJECT_TYPE", errUnion.getGreatestSubtype(STRING_OBJECT_TYPE));"""
        self.test_error_message = """expected:<[NoObject]> but was:<None>"""

class Framework(object):

    def reproduce_bug(self, bug_id):
        # Initialize and reproduce a bug using bug_id
        # Collect the bug info
        # create a Bug object and fill with bug info
        # return Bug object
        pass

    def run_test(self, patch=None):
        # Validate the patch (edit and rerun tests)
        # return TestResults object filled with test results

        # TODO: IMPORTANT IDEA
        # The patch should be cached with respect to the test suite it runs on
        # This way if the same patch is proposed multiple times that I do not
        # have to rerun the test suite again but could return the test result
        # immediately.

        if patch == "if (!result.isNoType()) {":
            return "PASS"
        elif patch == "if (!(result instanceof NoObjectType)) {":
            return "error: cannot find symbol (NoObjectType)"
        else:
            return self.test_error_message
