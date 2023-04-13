#!/usr/bin/expect -f

project_id=$1
bug_id=$2
version_id=${2}b
work_dir=$3
d4j_path=$4

export PATH=$PATH:$d4j_path

cd $work_dir

# Extract test error
test_error=$(exec sed '2!d' $work_dir/failing_tests) # grep second line of failing_test that contains the test error

#Output extracted data
echo $test_error