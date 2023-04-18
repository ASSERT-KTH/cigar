#!/usr/bin/expect -f

project_id=$1
bug_id=$2
version_id=${2}b
work_dir=$3
d4j_path=$4

cd $work_dir

# Extract test suite and test name
test_suite_and_name=$(exec sed '1!d' $work_dir/failing_tests | grep "\---") # Grep first line of failing_tests
test_suite_and_name=${test_suite_and_name/\---/} # Remove "---"
test_suite_and_name=${test_suite_and_name// /} # Remove "empty spaces"
test_suite=${test_suite_and_name%%::*} # Test suite is the part of test_suite_and_name before ::

# Extract test line
grep_test_suite=$test_suite
test_suite_count=$(exec less $work_dir/failing_tests | grep -c $grep_test_suite) # count the number of occurences of test_suite in failing_tests

if [ $test_suite_count -lt 2 ]; then # if test_suite_count occurs less than 2 times
    while [ $test_suite_count -lt 2 ]; do # while test_suite_count occurs less than 2 times
        grep_test_suite=${grep_test_suite%?} # remove the last character of grep_test_suite
        test_suite_count=$(exec less $work_dir/failing_tests | grep -c $grep_test_suite) # count the number of occurences of grep_test_suite in failing_tests
    done
fi

log_line_at_test_suite=$(exec less $work_dir/failing_tests | grep $grep_test_suite | sed '2!d') # grep line number of test suite
test_line_count=${log_line_at_test_suite##*:} # trim test_line_count to remove everything before :
test_line_count=${test_line_count%%)*} # trim test_line_count to remove everything after )

test_file_path=${log_line_at_test_suite#*at} # trim log_line_at_test_suite to remove everything before at
test_file_path=${test_file_path%%(*} # trim log_line_at_test_suite to remove everything after (
test_file_path=${test_file_path%.*} # trim log_line_at_test_suite to remove everything after the last .
test_file_path=${test_file_path//./\/} # change each . to / in test_file_path
test_file_path=$(echo $test_file_path | sed 's/ //g') # remove space from test_file_path

if [ $project_id = "Gson" ]; then
    test_file_path=$work_dir/gson/src/test/java/${test_file_path}.java
elif [ $project_id = "Chart" ]; then
    test_file_path=$work_dir/tests/${test_file_path}.java
elif [ $project_id = "Closure" ]; then
    test_file_path=$work_dir/test/${test_file_path}.java
elif [ $project_id = "Mockito" ]; then
    test_file_path=$work_dir/test/${test_file_path}.java
else
    test_file_path=$work_dir/src/test/java/${test_file_path}.java
fi

test_line=$(exec sed "${test_line_count}!d" $test_file_path)

#Output extracted data
echo $test_line