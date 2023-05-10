#!/usr/bin/expect -f

function reproduce_bug {
    project_id=$1
    bug_id=$2
    work_dir=$3
    d4j_path=$4

    echo "Reproducing bug $project_id $bug_id $work_dir $d4j_path"

    export PATH=$PATH:$d4j_path
    rm -rf $work_dir
    defects4j info -p $project_id -b $bug_id
    defects4j checkout -p $project_id -v "${bug_id}b" -w $work_dir

    cd $work_dir
    defects4j compile
    defects4j test -r
}

function get_bug_type {
    work_dir=$3
    cd $work_dir

    # Bug Types
    SINGLE_LINE="SL, SH, SF"
    SINGLE_HUNK="SH, SF"
    SINGLE_FUNCTION="SF"
    OTHER="OT"

    IFS='%' # preserve white spaces in code

    # Get git details
    git_show=$(git show)
    git_diff=$(git diff --stat HEAD^)

    # Export file_change_count from git_diff
    last_line=$(echo "$git_diff" | tail -n 1) # Get the last line of git_diff
    file_change_count=$(echo "$last_line" | awk '{print $1}') # Get the first column of the last line

    # Export line_change_count from git_diff
    second_line=$(echo "$git_diff" | head -n 2 | tail -n 1) # Get the second line of git_diff
    second_line=${second_line#*|} # remove everything before the | character
    line_change_count=$(echo "$second_line" | awk '{print $1}') # Get the first column of the second line

    # Get the code changes
    # TODO: The way I get the code below might not be correct, it may skip changes in one file in different locations
    code=${git_show##*@@ } # take the code from the last @@ sign until the end of file using
    numbered_list_of_changes=$(echo "$code" | grep -n -E '^\+|^-') # get a numbered list of lines that start with + and - 

    if [ $file_change_count -gt 2 ]; then
        bug_type=$OTHER # if file_change_count > 2, then it is OT
    elif [ $line_change_count -lt 2 ]; then
        bug_type=$SINGLE_LINE # else if line_change_count < 2, then it is SL
    elif [ $line_change_count -lt 3 ]; then
        first_line_count=$(echo "$numbered_list_of_changes" | head -n 1 | awk -F: '{print $1}')
        second_line_count=$(echo "$numbered_list_of_changes" | head -n 2 | tail -n 1 | awk -F: '{print $1}')
        diff=$((second_line_count - first_line_count))
        if [ $diff -eq 1 ]; then
            bug_type=$SINGLE_LINE
        else
            # TODO: Check if changes are in the same function -> SF, else OT
            bug_type=$OTHER
        fi
    else
        # TODO check if the bug is SH or SF

        bug_type=$OTHER
    fi

    # echo $code
    # echo ""
    echo $bug_type
}

function get_test_error {
    work_dir=$3

    cd $work_dir

    # Extract test error
    test_error=$(exec sed '2!d' $work_dir/failing_tests) # grep second line of failing_test that contains the test error

    #Output extracted data
    echo $test_error
}

function get_buggy_line {
    work_dir=$3
    cd $work_dir

    IFS='%' # preserve white spaces in code
    code=$(git show)
    code=${code##*@@} # take the code from the last @@ sign until the end of file using
    code=$(echo "$code" | sed '/^[^+]/d') # remove all lines that doesn't start with +
    code=$(echo "$code" | sed 's/^[+]//') # replace the + sign with nothing

    echo $code
}

function get_fixed_line {
    work_dir=$3
    cd $work_dir

    IFS='%' # preserve white spaces in code
    code=$(git show)
    code=${code##*@@} # take the code from the last @@ sign until the end of file using
    code=$(echo "$code" | sed '/^[^-]/d') # remove all lines that doesn't start with +
    code=$(echo "$code" | sed 's/^[-]//') # replace the + sign with nothing

    echo $code
}

function get_test_name {
    test_suite_and_name=$(get_test_suite_and_name $@)
    test_name=${test_suite_and_name##*::} # Test name is the part of test_suite_and_name after ::

    echo $test_name
}

function get_test_suite {
    test_suite_and_name=$(get_test_suite_and_name $@)
    test_suite=${test_suite_and_name%%::*} # Test suite is the part of test_suite_and_name before :: 
    echo $test_suite
}

function get_test_line {
    work_dir=$3
    cd $work_dir

    # Extract test suite and test name
    test_suite=$(get_test_suite $@)

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

    test_file_name=${log_line_at_test_suite#*at} # trim log_line_at_test_suite to remove everything before at
    test_file_name=${test_file_name%%(*} # trim log_line_at_test_suite to remove everything after (
    test_file_name=${test_file_name%.*} # trim log_line_at_test_suite to remove everything after the last .
    test_file_name=${test_file_name##*.} # trim log_line_at_test_suite to remove everything before last .

    test_file_path=$(exec find $work_dir | grep "/${test_file_name}.java" | sed '1!d') # find test_file_path

    test_line=$(exec sed "${test_line_count}!d" $test_file_path)

    echo $test_line
}

function get_code {
    work_dir=$3
    cd $work_dir

    IFS='%' # preserve white spaces in code

    git_diff_code=$(git show)

    code_change_line_count=$(echo "$git_diff_code" | grep -n "@@" | head -n 2 | tail -n 1 | cut -d: -f2-) # take the second line that starts with @@
    code_change_line_count=$(echo "$code_change_line_count" | cut -d- -f2-) # remove everything before the - sign in code_change_line_count
    code_change_line_count=$(echo "$code_change_line_count" | cut -d, -f1)
    code_change_line_count=$((code_change_line_count + 3))

    file_path=$(echo "$git_diff_code" | grep -n "diff" | head -n 2 | tail -n 1 | cut -d: -f2-) # take second line in code that starts with diff
    file_path=$(echo "$file_path" | rev | cut -d/ -f1 | rev) # remove everything before the last / symbol in file_path
    file_path=$(find $work_dir | grep "$file_path" | head -n 1) # take the first results of the grep search on file_path in work_dir

    # Find code_start_line_count
    for ((i=code_change_line_count;i>=0;i--)); do # for loop that goes from code_change_line_count down to 0
        line=$(sed -n "${i}p" $file_path) # take the line i in file_path
        if [[ $line == *"private"* ]] || [[ $line == *"protected"* ]] || [[ $line == *"public"* ]] || [[ $line == *"static"* ]] || [[ $line == *"void"* ]] || ([[ $line == *"JSType"* ]] && [[ $line == *"{"* ]]); then
            code_start_line_count=$i # set code_change_line_count to i
            break # break the loop
        fi
    done

    # Construct end_symbol
    start_line=$(sed -n "${code_start_line_count}p" $file_path) # read line code_start_line_count in file_path
    for ((i=0;i<${#start_line};i++)); do # get the index of the first non-whie space character in start_line
        if [[ ${start_line:$i:1} != " " ]]; then
            start_line_index=$i
            break
        fi
    done
    end_symbol=$(echo "${start_line:0:$start_line_index}}") # take the substring of start_line from 0 to start_line_index and append }

    # Find code_end_line_count
    for ((i=code_change_line_count;i<=((code_change_line_count + 1000));i++)); do # for loop that goes from code_change_line_count up to the end of the file
        line=$(sed -n "${i}p" $file_path) # take the line i in file_path
        if [[ $line == "${end_symbol}"* ]]; then # if line contains end_symbol
            code_end_line_count=$i # set code_end_line_count to i
            break # break the loop
        fi
    done

    # Read code
    code=$(sed -n "${code_start_line_count},${code_end_line_count}p" $file_path) # read file_path from code_start_line_count to code_end_line_count

    echo $code
}

function get_masked_code {
    work_dir=$3
    cd $work_dir

    IFS='%' # preserve white spaces in code

    # Read Code
    code=$(get_code $@)

    git_diff=$(git show)
    git_diff_code=${git_diff##*@@} # take the code from the last @@ sign until the end of file using

    # Find line count of git diff
    code_change_line_count=$(echo "$git_diff" | grep -n "@@" | head -n 2 | tail -n 1 | cut -d: -f2-) # take the second line that starts with @@
    code_change_line_count=$(echo "$code_change_line_count" | cut -d- -f2-) # remove everything before the - sign in code_change_line_count
    code_change_line_count=$(echo "$code_change_line_count" | cut -d, -f1)
    code_change_line_count=$((code_change_line_count + 3))

    # Find source code file patch
    file_path=$(echo "$git_diff" | grep -n "diff" | head -n 2 | tail -n 1 | cut -d: -f2-) # take second line in code that starts with diff
    file_path=$(echo "$file_path" | rev | cut -d/ -f1 | rev) # remove everything before the last / symbol in file_path
    file_path=$(find $work_dir | grep "$file_path" | head -n 1) # take the first results of the grep search on file_path in work_dir

    # Find code_start_line_count
    for ((i=code_change_line_count;i>=0;i--)); do # for loop that goes from code_change_line_count down to 0
        line=$(sed -n "${i}p" $file_path) # take the line i in file_path
        if [[ $line == *"private"* ]] || [[ $line == *"protected"* ]] || [[ $line == *"public"* ]] || [[ $line == *"static"* ]] || [[ $line == *"void"* ]] || ([[ $line == *"JSType"* ]] && [[ $line == *"{"* ]]); then
            code_start_line_count=$i # set code_start_line_count to i
            break # break the loop
        fi
    done

    # Remove buggy lines
    buggy_lines=$(echo "$git_diff_code" | grep "^+" | sed 's/^+//g') # grep lines that start with + symbol
    masked_code=$code
    for buggy_line in $buggy_lines # for each buggy_line in buggy_lines remove the buggy_line from code
    do
        buggy_line=$(echo "$buggy_line" | sed 's/^+//g') # remove the starting + symbol
        masked_code=$(echo "$masked_code" | sed "/^${buggy_line}$/d") # using sed delete the line that starts with buggy_line
    done

    # Create masked_code
    local_buggy_line_count=$((code_change_line_count - code_start_line_count + 1)) # line after the change
    masked_code=$(echo "$masked_code" | sed "${local_buggy_line_count}s/^/INFILL\n&/") 

    echo $masked_code
}

function validate_patch {
    set -e

    work_dir=$3
    d4j_path=$4
    patch=$5

    IFS='%' # preserve white spaces in code
    export PATH=$PATH:$d4j_path
    cd $work_dir

    # Restore original git state
    git restore .

    # Export buggy line
    buggy_line=$(git show)
    buggy_line=${buggy_line##*@@} # take the code from the last @@ sign until the end of file using
    buggy_line=$(echo "$buggy_line" | sed '/^[^+]/d') # remove all lines that doesn't start with +
    buggy_line=$(echo "$buggy_line" | sed 's/^[+]//') # replace the + sign with nothing

    # Extract buggy code path
    code_file_path=$(git show | grep "+++" | sed '2!d')
    code_file_path=${code_file_path#*+++} # trim code_file_path to remove everything before +++
    code_file_path=${code_file_path#*/} # remove everything before the first / in code_file_path
    code_file_path=$work_dir/$code_file_path

    # Get the line number of the buggy line
    line_number=$(grep -n "$buggy_line" $code_file_path | cut -d: -f1)

    # Remove line at line_number (buggy line)
    cp $code_file_path ${code_file_path}.tmp &&
    sed "${line_number}d" <${code_file_path}.tmp >$code_file_path &&
    rm -f ${code_file_path}.tmp
    # Remove patch at line_number
    cp $code_file_path ${code_file_path}.tmp
    awk -v line_number="$line_number" -v patch="$patch" 'NR==line_number{print patch}1' ${code_file_path}.tmp > $code_file_path
    rm -f ${code_file_path}.tmp

    defects4j compile

    defects4j test -r
}

# ---------- UTILS -------------

function get_test_suite_and_name {
    work_dir=$3
    cd $work_dir

    # Extract test suite and test name
    test_suite_and_name=$(exec sed '1!d' $work_dir/failing_tests | grep "\---") # Grep first line of failing_tests
    test_suite_and_name=${test_suite_and_name/\---//} # Remove "---"
    test_suite_and_name=${test_suite_and_name///} # Remove "empty spaces"

    echo $test_suite_and_name
}

# ------------------------------

if declare -f "$1" > /dev/null
then
  # call arguments verbatim
  "$@"
else
  # Show a helpful error
  echo "'$1' is not a known function name" >&2
  exit 1
fi