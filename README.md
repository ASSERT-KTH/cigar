# Conversational Automated Program Repair


## Tasks

- [ ] Reproduce the process and results of [this](https://docs.gitlab.com/ee/user/project/repository/web_editor.html#upload-a-file) paper


## Reproducability

### Setup Pre-requisites

Make sure defects4j is setup on your computer properly and you can checkout any active bug in Chart, Closure, Lang, Math, Mockito and Time projects.

- For Chart bugs you may need to install svn
```
sudo apt-get install subversion
```

### Setup CAPR

Steps to reproduce the results:

- Clone the repo, cd into folder
```
git clone git@github.com:ASSERT-KTH/capr.git
cd capr
```

- Create a virtualenv for the repo, activate it
```
virtualenv venv
source venv/bin/activate
```

- Install the requiremets
```
pip install -r requirements.txt
```

- Duplicate the `user_params.py.template` file in root folder, name the duplicate file `user_params.py`

- Set the `TMP_DIR` (path to checkout the bugs to), `JAVA_HOME` (path to Java home directory) `D4J_PATH` (path that points to your defects4j/framework/bin) and `API_KEY` (your openai api key) in the `user_params.py` file

- Now you can run capr.py with the following command
```
$(pwd)/venv/bin/python3 "$(pwd)/main.py"
```

## Tests

To test your `TMP_DIR` and `D4J_PATH` settings, you can run the following command from the root folder.

```
TMP_DIR=$(grep TMP_DIR user_params.py | grep -o '".*"' | sed 's/"//g')
JAVA_HOME=$(grep JAVA_HOME user_params.py | grep -o '".*"' | sed 's/"//g')
D4J_PATH=$(grep D4J_PATH user_params.py | grep -o '".*"' | sed 's/"//g')

bug_id=1
project="Time"
command="checkout_bug"
work_dir="$TMP_DIR/$project-$bug_id/"
java_home="$JAVA_HOME"
d4j_path="$D4J_PATH"

cd frameworks
bash defects4j.sh "$command" "$project" "$bug_id" "$work_dir" "$java_home" "$d4j_path"
cd -
```
After running the command above you should see the following console output:
```
Check out program version: Time-1b......................................... OK
```
And you should find the bug in the `$TMP_DIR` folder, that you've set.

## Continuous Running

### Run in a loop

As explained [here](https://stackoverflow.com/questions/696839/how-do-i-write-a-bash-script-to-restart-a-process-if-it-dies) you can start the script in a loop, so that it restarts if it crashes. (Which happens often with the openai api)

```
project="Chart" 
until $(pwd)/venv/bin/python3 "$(pwd)/main.py" -p $project; do
    echo "CAPR crashed with exit code $?. Restaring in a second..."
    sleep 1
done
```

### Running in parallel

Using GNU Parallel you can run multiple instances of the script in parallel. You can install it with `sudo apt-get install parallel`

```
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
```

Reference: Tange, O. (2023, May 22). GNU Parallel 20230522 ('Charles'). Zenodo. https://doi.org/10.5281/zenodo.7958356

```
@software{tange_2023_7958356,
      author       = {Tange, Ole},
      title        = {GNU Parallel 20230522 ('Charles')},
      month        = May,
      year         = 2023,
      note         = {{GNU Parallel is a general parallelizer to run
                       multiple serial command line programs in parallel
                       without changing them.}},
      publisher    = {Zenodo},
      doi          = {10.5281/zenodo.7958356},
      url          = {https://doi.org/10.5281/zenodo.7958356}
}
```