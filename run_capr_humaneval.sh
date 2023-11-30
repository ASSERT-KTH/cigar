export num_of_parallel_jobs=8
export apr="capr"
export framework="humanevaljava"
export output_dir="output/${framework}_${apr}"

declare -a pool=("humaneval")
declare -a humaneval=("ADD" "ADD_ELEMENTS" "ADD_EVEN_AT_ODD" "ALL_PREFIXES" "ANTI_SHUFFLE" "ANY_INT" "BELOW_THRESHOLD" "BELOW_ZERO" "BF" "BY_LENGTH" "CAN_ARRANGE" "CAR_RACE_COLLISION" "CHANGE_BASE" "CHECK_DICT_CASE" "CHECK_IF_LAST_CHAR_IS_A_LETTER" "CHOOSE_NUM" "CIRCULAR_SHIFT" "CLOSEST_INTEGER" "COMMON" "COMPARE" "COMPARE_ONE" "CONCATENATE" "CORRECT_BRACKETING" "COUNT_DISTINCT_CHARACTERS" "COUNT_NUMS" "COUNT_UPPER" "COUNT_UP_TO" "CYCPATTERN_CHECK" "DECIMAL_TO_BINARY" "DECODE_CYCLIC" "DECODE_SHIFT" "DERIVATIVE" "DIGITS" "DIGIT_SUM" "DOUBLE_THE_DIFFERENCE" "DO_ALGEBRA" "EAT" "ENCODE" "ENCRYPT" "EVEN_ODD_COUNT" "EVEN_ODD_PALINDROME" "EXCHANGE" "FACTORIAL" "FACTORIZE" "FIB" "FIB4" "FIBFIB" "FILE_NAME_CHECK" "FILTER_BY_PREFIX" "FILTER_BY_SUBSTRING" "FILTER_INTEGERS" "FIND_CLOSEST_ELEMENTS" "FIND_ZERO" "FIX_SPACES" "FIZZ_BUZZ" "FLIP_CASE" "FRUIT_DISTRIBUTION" "GENERATE_INTEGERS" "GET_CLOSET_VOWEL" "GET_MAX_TRIPLES" "GET_ODD_COLLATZ" "GET_POSITIVE" "GET_ROW" "GREATEST_COMMON_DIVISOR" "HAS_CLOSE_ELEMENTS" "HEX_KEY" "HISTOGRAM" "HOW_MANY_TIMES" "INCR_LIST" "INTERSECTION" "INTERSPERSE" "INT_TO_MINI_ROMAN" "ISCUBE" "IS_BORED" "IS_EQUAL_TO_SUM_EVEN" "IS_HAPPY" "IS_MULTIPLY_PRIME" "IS_NESTED" "IS_PALINDROME" "IS_PRIME" "IS_SIMPLE_POWER" "IS_SORTED" "LARGEST_DIVISOR" "LARGEST_PRIME_FACTOR" "LARGEST_SMALLEST_INTEGERS" "LONGEST" "MAKE_A_PILE" "MAKE_PALINDROME" "MATCH_PARENS" "MAXIMUM_K" "MAX_ELEMENT" "MAX_FILL" "MEAN_ABSOLUTE_DEVIATION" "MEDIAN" "MIN_PATH" "MIN_SUBARRAY_SUM" "MODP" "MONOTONIC" "MOVE_ONE_BALL" "MULTIPLY" "NEXT_SMALLEST" "NUMERICAL_LETTER_GRADE" "ODD_COUNT" "ORDER_BY_POINTS" "PAIRS_SUM_TO_ZERO" "PARSE_MUSIC" "PARSE_NESTED_PARENS" "PLUCK" "PRIME_FIB" "PRIME_LENGTH" "PROD_SIGNS" "REMOVE_DUPLICATES" "REMOVE_VOWELS" "RESCALE_TO_UNIT" "REVERSE_DELETE" "RIGHT_ANGLE_TRIANGLE" "ROLLING_MAX" "ROUNDED_AVG" "SAME_CHARS" "SEARCH" "SELECT_WORDS" "SEPARATE_PAREN_GROUPS" "SIMPLIFY" "SKJKASDKD" "SMALLEST_CHANGE" "SOLUTION" "SOLVE" "SOLVE_STRING" "SORTED_LIST_SUM" "SORT_ARRAY" "SORT_ARRAY_BINARY" "SORT_EVEN" "SORT_NUMBERS" "SORT_THIRD" "SPECIAL_FACTORIAL" "SPECIAL_FILTER" "SPLIT_WORDS" "STARTS_ONE_ENDS" "STRANGE_SORT_LIST" "STRING_SEQUENCE" "STRING_TO_MD5" "STRING_XOR" "STRLEN" "STRONGEST_EXTENSION" "SUM_PRODUCT" "SUM_SQUARED_NUMS" "SUM_SQUARES" "SUM_TO_N" "TOTAL_MATCH" "TRI" "TRIANGLE_AREA" "TRIANGLE_AREA_2" "TRIPLES_SUM_TO_ZERO" "TRUNCATE_NUMBER" "UNIQUE" "UNIQUE_DIGITS" "VALID_DATE" "VOWELS_COUNT" "WILL_IT_FLY" "WORDS_IN_SENTENCE" "WORDS_STRINGS" "X_OR_Y")


# Prepare run params
n=0
declare -a params_bug_ids
declare -a params_projects
for group in "${pool[@]}"; do
    lst="$group[@]"
    for element in "${!lst}"; do
        params_i[$n]=$n
        params_projects[$n]=$group
        params_bug_ids[$n]=$element
        n=$((n+1))
    done
done

# Remove existing parallel folder and files
rm -rf parallel_results
rm -rf parallel.log


# For each project, keep only the first line of the csv file
for project in "${pool[@]}"; do
    head -n 1 "${output_dir}/${project}_summary.csv" > "${output_dir}/${project}_summary.csv.tmp"
    mv "${output_dir}/${project}_summary.csv.tmp" "${output_dir}/${project}_summary.csv"
done


# Function to run a single project, in case of crash, restart
run_project_bug() {
    project=$1
    bug=$2
    # make apr all lower case
    apr=$(echo "$apr" | tr '[:upper:]' '[:lower:]')
    until python main.py -apr $apr -fr $framework -p $project -bs $bug; do 
        echo "CAPR crashed with exit code $?. Restaring in a minute..."
        sleep 60
    done
}
export -f run_project_bug
# Run each bug in parallel
parallel --jobs $num_of_parallel_jobs --bar --joblog parallel.log --results parallel_results/ --resume --resume-failed run_project_bug {1} {2} ::: "${params_projects[@]}" :::+ "${params_bug_ids[@]}"


# For each project order the summary file by bug id, first line is header
for project in "${pool[@]}"; do
    tail -n +1 "${output_dir}/${project}_summary.csv" | sort -t, -k3,3n > "${output_dir}/${project}_summary.csv.tmp"
    head -n 1 "${output_dir}/${project}_summary.csv" > "${output_dir}/${project}_summary.csv"
    cat "${output_dir}/${project}_summary.csv.tmp" >> "${output_dir}/${project}_summary.csv"
    rm "${output_dir}/${project}_summary.csv.tmp"
done

# Merge all summary files into one, first line is the header
head -n 1 "${output_dir}/${pool[0]}_summary.csv" > "${output_dir}/summary.csv"
for project in "${pool[@]}"; do
    tail -n +2 "${output_dir}/${project}_summary.csv" >> "${output_dir}/summary.csv"
done