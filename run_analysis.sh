num_of_parallel_jobs=16
project="Chart" 
bug_ids=(1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26)

for i in {1..5}
do
    parallel --jobs $num_of_parallel_jobs --bar --joblog parallel_${project}.log --results parallel_results_${project}/ --resume --resume-failed $(pwd)/venv/bin/python3 $(pwd)/main.py -p $project -bs {} ::: "${bug_ids[@]}"

    rm -rf parallel_results_${project}/
    rm parallel_${project}.log
done

until $(pwd)/venv/bin/python3 "$(pwd)/main.py" -p $project; do
    echo "CAPR crashed with exit code $?. Restaring in a second..."
    sleep 1
done



num_of_parallel_jobs=16
project="Closure" 
bug_ids=(1 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 19 20 21 22 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 40 41 42 43 44 45 46 47 48 49 50 51 52 54 55 56 57 58 59 60 61 62 64 65 66 67 68 69 70 71 72 73 74 75 76 77 79 80 81 82 83 84 85 86 87 88 89 90 91 92 94 95 96 97 98 99 100 101 102 103 104 105 106 107 108 110 111 112 113 114 115 116 117 118 119 120 121 122 123 125 126 127 128 129 130 131 132 133 134 135 136 137 138 140 141 142 143 144 145 146 147 148 149 150 151 152 153 154 156 157 158 159 160 161 162 163 164 165 166 167 168 169 171 172 173 174 175 176)

for i in {1..5}
do
    parallel --jobs $num_of_parallel_jobs --bar --joblog parallel_${project}.log --results parallel_results_${project}/ --resume --resume-failed $(pwd)/venv/bin/python3 $(pwd)/main.py -p $project -bs {} ::: "${bug_ids[@]}"

    rm -rf parallel_results_${project}/
    rm parallel_${project}.log
done

until $(pwd)/venv/bin/python3 "$(pwd)/main.py" -p $project; do
    echo "CAPR crashed with exit code $?. Restaring in a second..."
    sleep 1
done




num_of_parallel_jobs=16
project="Lang" 
bug_ids=(1 3 4 5 6 7 8 9 10 11 12 13 14 15 16 18 19 20 21 22 23 24 25 26 27 28 29 30 32 33 34 35 36 37 38 39 40 41 42 43 44 46 47 48 49 50 52 53 54 55 56 57 58 59 60 61 62 63 64)

for i in {1..5}
do
    parallel --jobs $num_of_parallel_jobs --bar --joblog parallel_${project}.log --results parallel_results_${project}/ --resume --resume-failed $(pwd)/venv/bin/python3 $(pwd)/main.py -p $project -bs {} ::: "${bug_ids[@]}"

    rm -rf parallel_results_${project}/
    rm parallel_${project}.log
done

until $(pwd)/venv/bin/python3 "$(pwd)/main.py" -p $project; do
    echo "CAPR crashed with exit code $?. Restaring in a second..."
    sleep 1
done



num_of_parallel_jobs=8
project="Math"
bug_ids=(1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64 65 66 67 68 69 70 71 72 73 74 75 76 77 78 79 80 81 82 83 84 85 86 87 88 89 90 91 92 93 94 95 96 97 98 99 100 101 102 103 104 105 106)

for i in {1..5}
do
    parallel --jobs $num_of_parallel_jobs --bar --joblog parallel_${project}.log --results parallel_results_${project}/ --resume --resume-failed $(pwd)/venv/bin/python3 $(pwd)/main.py -p $project -bs {} ::: "${bug_ids[@]}"

    rm -rf parallel_results_${project}/
    rm parallel_${project}.log
done

until $(pwd)/venv/bin/python3 "$(pwd)/main.py" -p $project; do
    echo "CAPR crashed with exit code $?. Restaring in a second..."
    sleep 1
done



num_of_parallel_jobs=8
project="Mockito"
bug_ids=(1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 17 18 19 20 21 22 23 24 25 26 27 28 29 31 32 33 34 35 36 37 38)

for i in {1..5}
do
    parallel --jobs $num_of_parallel_jobs --bar --joblog parallel_${project}.log --results parallel_results_${project}/ --resume --resume-failed $(pwd)/venv/bin/python3 $(pwd)/main.py -p $project -bs {} ::: "${bug_ids[@]}"

    rm -rf parallel_results_${project}/
    rm parallel_${project}.log
done

until $(pwd)/venv/bin/python3 "$(pwd)/main.py" -p $project; do
    echo "CAPR crashed with exit code $?. Restaring in a second..."
    sleep 1
done



num_of_parallel_jobs=8
project="Time"
bug_ids=(1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 22 23 24 25 26 27)

for i in {1..5}
do
    parallel --jobs $num_of_parallel_jobs --bar --joblog parallel_${project}.log --results parallel_results_${project}/ --resume --resume-failed $(pwd)/venv/bin/python3 $(pwd)/main.py -p $project -bs {} ::: "${bug_ids[@]}"

    rm -rf parallel_results_${project}/
    rm parallel_${project}.log
done

until $(pwd)/venv/bin/python3 "$(pwd)/main.py" -p $project; do
    echo "CAPR crashed with exit code $?. Restaring in a second..."
    sleep 1
done