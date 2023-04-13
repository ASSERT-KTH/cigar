#!/usr/bin/expect -f

project_id=$1
bug_id=$2
version_id=${2}b
work_dir=$3
d4j_path=$4

export PATH=$PATH:$d4j_path

cd $work_dir

# Extract test suite and test name
test_suite_and_name=$(exec sed '1!d' $work_dir/failing_tests | grep "\---") # Grep first line of failing_tests
test_suite_and_name=${test_suite_and_name/\---//} # Remove "---"
test_suite_and_name=${test_suite_and_name///} # Remove "empty spaces"
test_name=${test_suite_and_name##*::} # Test name is the part of test_suite_and_name after ::

#Output extracted data
echo $test_name