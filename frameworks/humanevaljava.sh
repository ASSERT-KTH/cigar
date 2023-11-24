#!/usr/bin/expect -f

function checkout_bug {
    bug_id=$2
    work_dir=$3
    d4j_path=$5

    rm -rf $work_dir
    cp -r $d4j_path $work_dir
}

function compile_and_run_tests {
    bug_id=$2
    work_dir=$3
    java_home=$4
    d4j_path=$5
    
    cd $work_dir
    
    export JAVA_HOME=$java_home
    timeout_seconds=600
    custom_timeout $timeout_seconds "mvn test -Dtest=TEST_$bug_id"
}

function get_bug_type {
    echo "SF"
}

function get_test_error {
    bug_id=$2
    work_dir=$3
    cd $work_dir

    export JAVA_HOME=$java_home
    timeout_seconds=600

    # Extract test error
    test_error=$(timeout $timeout_seconds mvn test -Dtest=TEST_$bug_id | sed -n '/\[ERROR\] Failures:/{n;p}' | sed 's/\[ERROR\]//')

    #Output extracted data
    echo $test_error
}

function get_buggy_lines {
    bug_id=$2
    work_dir=$3
    cd $work_dir

    sed -i 's/package humaneval\\.correct/package humaneval\\.buggy/g' src/main/java/humaneval/correct/$bug_id.java

    IFS='∫' # preserve white spaces in code
    code=$(diff --unified src/main/java/humaneval/buggy/$bug_id.java src/main/java/humaneval/correct/$bug_id.java)
    code=${code##*@@} # take the code from the last @@ sign until the end of file using
    code=$(echo "$code" | sed '/^[^-]/d') # remove all lines that doesn't start with -
    code=$(echo "$code" | sed 's/^[-]//') # replace the - sign with nothing

    sed -i 's/package humaneval\\.buggy/package humaneval\\.correct/g' src/main/java/humaneval/correct/$bug_id.java

    echo $code
}

function get_fixed_lines {
    bug_id=$2
    work_dir=$3
    cd $work_dir

    sed -i 's/package humaneval\\.correct/package humaneval\\.buggy/g' src/main/java/humaneval/correct/$bug_id.java

    IFS='∫' # preserve white spaces in code
    code=$(diff --unified src/main/java/humaneval/buggy/$bug_id.java src/main/java/humaneval/correct/$bug_id.java)
    code=${code##*@@} # take the code from the last @@ sign until the end of file using
    code=$(echo "$code" | sed '/^[^+]/d') # remove all lines that doesn't start with +
    code=$(echo "$code" | sed 's/^[+]//') # replace the + sign with nothing

    sed -i 's/package humaneval\\.buggy/package humaneval\\.correct/g' src/main/java/humaneval/correct/$bug_id.java

    echo $code
}

function get_test_name {
    bug_id=$2
    work_dir=$3
    cd $work_dir

    export JAVA_HOME=$java_home
    timeout_seconds=600

    # Extract test error
    test_error=$(timeout $timeout_seconds mvn test -Dtest=TEST_$bug_id | sed -n '/\[ERROR\] Failures:/{n;p}' | sed 's/\[ERROR\]//')

    # Extract test name
    test_name=${test_error%%:*} # Test name is the part of test_error before :
    test_name=${test_name##*.} # Test name is the part of test_name after .

    #Output extracted data
    echo $test_name
}

function get_test_suite {
    bug_id=$2
    work_dir=$3
    cd $work_dir

    export JAVA_HOME=$java_home
    timeout_seconds=600

    # Extract test error
    test_error=$(timeout $timeout_seconds mvn test -Dtest=TEST_$bug_id | sed -n '/\[ERROR\] Failures:/{n;p}' | sed 's/\[ERROR\]//')

    # Extract test name
    test_name=${test_error%%.*} # Test name is the part of test_error before :

    #Output extracted data
    echo $test_name
}

function get_test_line {
    bug_id=$2
    work_dir=$3
    cd $work_dir

    IFS='∫' # preserve white spaces in code
    export JAVA_HOME=$java_home
    timeout_seconds=600

    # Extract test error
    test_error=$(timeout $timeout_seconds mvn test -Dtest=TEST_$bug_id | sed -n '/\[ERROR\] Tests run:/{n;p;n;p;n;p}')

    # Extract portion with file name and number
    test_error=${test_error##*at} # take everything after "at"
    file_name=${test_error##*\(} # take everything after "("
    file_name=${file_name%%:*} # take everything before ":"
    line_number=${test_error##*:} # take everything after ":"
    line_number=${line_number%%)*} # take everything before ")"

    file_name="src/test/java/humaneval/$file_name"

    # if test_file_path is not empty and test_line_count is not empty
    if [ ! -z "$file_name" ] && [ ! -z "$line_number" ]; then
        test_line=$(exec sed "${line_number}!d" $file_name)
    fi

    echo $test_line
}

function get_code {
    work_dir=$3
    cd $work_dir

    IFS='∫' # preserve white spaces in code

    code_block=$(get_git_show_function_code $@) # Get function code from git show that contains the changes

    code=$(echo "$code_block" | sed '/^[-]/d') # Remove lines that start with -
    code=$(echo "$code" | sed '/^[+]/s/+/ /') # Replace + with space in lines that start with +
    code=$(echo "$code" | sed 's/^[[:space:]]//') # Remove first leading white spaces

    echo $code
}

function get_masked_code {
    work_dir=$3
    cd $work_dir

    IFS='∫' # preserve white spaces in code

    code_block=$(get_git_show_function_code $@) # Get function code from git show that contains the changes

    # Replace the every line staring with - with INFILL
    masked_code=$(echo "$code_block" | sed '/^[+-]/s/[+-].*/INFILL/')
    
    # Keep only the lines that start with INFILL
    number_of_lines_starting_with_infill=$(echo "$masked_code" | grep -c INFILL) # Count the number of lines starting with INFILL
    for (( i=2; i<=$number_of_lines_starting_with_infill; i++ )); do
        first_infill_line_count=$(echo "$masked_code" | grep -n INFILL | sed '1!d' | cut -d: -f1) # Get the line number of the first line starting with INFILL
        masked_code=$(echo "$masked_code" | sed "${first_infill_line_count}d") # remove the line at first_infill_line_count
    done

    masked_code=$(echo "$masked_code" | sed 's/INFILL/>>> [ INFILL ] <<</')
    masked_code=$(echo "$masked_code" | sed 's/^[[:space:]]//') # Remove first leading white spaces

    echo $masked_code
}

function get_fixed_code {
    work_dir=$3
    cd $work_dir

    IFS='∫' # preserve white spaces in code

    code_block=$(get_git_show_function_code $@) # Get function code from git show that contains the changes

    code=$(echo "$code_block" | sed '/^[+]/d') # Remove lines that start with +
    code=$(echo "$code" | sed '/^[-]/s/-/ /') # Replace - with space in lines that start with -
    code=$(echo "$code" | sed 's/^[[:space:]]//') # Remove first leading white spaces

    echo $code
}

function validate_patch {
    set -e

    bug_id=$2
    work_dir=$3
    d4j_path=$5
    patch=$6
    mode=$7

    IFS='∫' # preserve white spaces in code
    cd $work_dir

    # Construct patch_function
    if [[ $mode == "SF" ]]; then
        patch_function=$patch
    else
        masked_code=$(get_masked_code $@)
        patch_function="${masked_code//\>\>\> \[ INFILL \] \<\<\</${patch}}"
    fi

    # Extract buggy code path
    code_file_path=$(get_source_code_file_path $@)

    # Put patch_function in place of the buggy function in code_file_path
    full_code=$(less $code_file_path)    
    code_function=$(get_code $@)
    code_function_length=$(echo "$code_function" | wc -l | sed 's/^[ \t]*//;s/[ \t]*$//')
    code_function_first_line=$(echo "$code_function" | head -n 1)

    # Find first and last line numbers of the function in which the change was made
    first_change_line_count_number=$(get_first_change_line_count_number $@)
    code_block=$(less $code_file_path)
    code_function_first_line_number=$(get_function_line_count_from_line_in_code_block $first_change_line_count_number)
    code_function_last_line_number=$((code_function_first_line_number + code_function_length - 1))

    full_code_without_buggy_function=$(echo "$full_code" | sed "${code_function_first_line_number},${code_function_last_line_number}d")

    prefix=$(echo "$full_code_without_buggy_function" | head -n $((code_function_first_line_number - 1)))
    suffix=$(echo "$full_code_without_buggy_function" | tail -n +$((code_function_first_line_number)))

    line_above_code_function_first_line_number=$(echo "$full_code" | sed "$((code_function_first_line_number - 1))!d") # Line above the code_function_first_line_number
    if [[ $line_above_code_function_first_line_number =~ ^[[:space:]]*$ ]]; then # Check if line contains only white spaces
        patch_function="
${patch_function}"
    fi

    patched_full_code="${prefix}
${patch_function}
${suffix}"
    echo "$patched_full_code" > ${code_file_path}

    # Compile and run test
    compile_and_run_tests $@
}

function get_patch_git_diff {
    set -e

    work_dir=$3
    d4j_path=$5

    IFS='∫' # preserve white spaces in code
    cd $work_dir

    # Get code path
    code_file_path=$(get_source_code_file_path $@)

    # export diff file of code_file_path to diff_file_path
    echo $(git diff $code_file_path)
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

function get_source_code_file_path {
    bug_id=$2
    work_dir=$3
    cd $work_dir

    echo "src/main/java/humaneval/buggy/$bug_id.java"
}

function is_list_continuous {
    list=$1
    list_len=$(echo "$list" | wc -l | sed 's/^[ \t]*//;s/[ \t]*$//')
    is_continuous=1
    for ((i=1;i<$list_len;i++)); do
        list_i=$(echo ${list} | head -n ${i} | tail -n 1)
        list_i_p1=$(echo ${list} | head -n $((i + 1)) | tail -n 1)
        if [[ $((list_i + 1)) != $((list_i_p1)) ]]; then
            is_continuous=0
            break
        fi
    done
    echo $is_continuous
}

function is_function_line {
    line=$1
    trimmed_line=$(echo "${line}" | sed 's/^[ \t]*//') # remove empty white spaces from beginning of line
    is_function=0

    if [[ $trimmed_line != "//"* ]]; then
        if [[ $trimmed_line == *"("* ]] && ([[ $trimmed_line == *"private"* ]] || [[ $trimmed_line == *"protected"* ]] || [[ $trimmed_line == *"public"* ]] || [[ $trimmed_line == *"static"* ]] || [[ $trimmed_line == *"void"* ]]); then
            is_function=1
        elif  [[ $trimmed_line == *"JSType"* ]] && [[ $trimmed_line == *"{"* ]]; then
            is_function=1
        elif  [[ $trimmed_line == *"class"* ]] && [[ $trimmed_line == *"{"* ]]; then
            is_function=1
        fi
    fi

    echo ${is_function}
}

function get_function_line_from_line_in_code_block {
    from_line=$1

    for ((i=$from_line;i>=0;i--)); do # for loop that goes from from_line down to 0
        line=$(echo "$code_block" | sed -n "${i}p") # take the line i in text
        if [[ $(is_function_line $line) == 1 ]]; then
            break
        fi
    done

    echo ${line}
}

function get_function_line_count_from_line_in_code_block {
    from_line=$1

    for ((i=$from_line;i>=0;i--)); do # for loop that goes from from_line down to 0
        line=$(echo "$code_block" | sed -n "${i}p") # take the line i in text
        if [[ $(is_function_line $line) == 1 ]]; then
            line_count=${i}
            break
        fi
    done
    
    echo ${line_count}
}

function get_first_change_line_count_number {
    bug_id=$2
    work_dir=$3
    cd $work_dir

    IFS='∫'

    sed -i 's/package humaneval\\.correct/package humaneval\\.buggy/g' src/main/java/humaneval/correct/$bug_id.java
    git_show=$(diff --unified src/main/java/humaneval/correct/$bug_id.java src/main/java/humaneval/buggy/$bug_id.java)
    sed -i 's/package humaneval\\.buggy/package humaneval\\.correct/g' src/main/java/humaneval/correct/$bug_id.java
    
    first_change_line_count_number=$(echo "$git_show" | grep "^@@" | head -n 2 | tail -n 1) # take the second line that starts with @@
    first_change_line_count_number=${first_change_line_count_number//@@/} # remove @@
    first_change_line_count_number=$(echo "${first_change_line_count_number}" | sed 's/^[ \t]*//') # remove space from beginning of line
    first_change_line_count_number=$(echo "${first_change_line_count_number}" | cut -d' ' -f1) # remove everything after the first space
    first_change_line_count_number=$(echo "${first_change_line_count_number}" | sed 's/^[+-]//')

    echo $first_change_line_count_number
}

function get_git_show_function_code {
    IFS='∫'

    bug_id=$2
    work_dir=$3
    cd $work_dir

    sed -i 's/package humaneval\\.correct/package humaneval\\.buggy/g' src/main/java/humaneval/correct/$bug_id.java
    git_show=$(diff --unified src/main/java/humaneval/correct/$bug_id.java src/main/java/humaneval/buggy/$bug_id.java)
    sed -i 's/package humaneval\\.buggy/package humaneval\\.correct/g' src/main/java/humaneval/correct/$bug_id.java
    git_diff_code=${git_show##*@@} # take the code from the last @@ sign until the end of file using
    code_block=$(echo $git_diff_code)

    # get first line that starts with + or -
    code_change_line_count=$(echo "$code_block" | grep -n -m 1 "^[+-]" | cut -d: -f1)

    # Find code_start_line_count
    code_start_line=$(get_function_line_from_line_in_code_block $code_change_line_count)
    code_start_line_count=$(get_function_line_count_from_line_in_code_block $code_change_line_count)

    # Construct end_symbol
    start_line=${code_start_line}
    for ((i=0;i<${#start_line};i++)); do # get the index of the first non-whie space character in start_line
        if [[ ${start_line:$i:1} != " " ]]; then
            start_line_index=$i
            break
        fi
    done
    end_symbol=$(echo "${start_line:0:$start_line_index}}") # take the substring of start_line from 0 to start_line_index and append }

    # Find code_end_line_count
    for ((i=code_change_line_count;i<=((code_change_line_count + 1000));i++)); do # for loop that goes from code_change_line_count up to the end of the file
        line=$(echo "$code_block" | sed "${i}!d") # get line i from code_block
        if [[ $line == "${end_symbol}"* ]]; then # if line contains end_symbol
            code_end_line_count=$i # set code_end_line_count to i
            break # break the loop
        fi
    done

    code_block=$(echo "$code_block" | sed -n "${code_start_line_count},${code_end_line_count}p") # take the lines from code_start_line_count to code_end_line_count from code_block

    echo ${code_block}
}

# From https://unix.stackexchange.com/questions/43340/how-to-introduce-timeout-for-shell-scripting
################################################################################
# Executes command with a timeout
# Params:
#   $1 timeout in seconds
#   $2 command
# Returns 1 if timed out 0 otherwise
function custom_timeout {

    time=$1

    # start the command in a subshell to avoid problem with pipes
    # (spawn accepts one command)
    command="/bin/bash -c \"$2\""

    expect -c "set echo \"-noecho\"; set timeout $time; spawn -noecho $command; expect timeout { exit 1 } eof { exit 0 }"    

    if [ $? = 1 ] ; then
        exit 1
    fi

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