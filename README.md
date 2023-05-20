# Conversational Automated Program Repair


## Tasks

- [ ] Reproduce the process and results of [this](https://docs.gitlab.com/ee/user/project/repository/web_editor.html#upload-a-file) paper


## Reproducability

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

- Add openai key to `openai_api_key.env` file in root folder of capr

- Set the `TMP_DIR` (path to checkout the bugs to) and `D4J_PATH` (path that points to your defects4j/framework/bin) in the params.py file

- Run the following command with your `TMP_DIR` and `D4J_PATH` to check if everything was setup properly

```
TMP_DIR="/tmp/defects4j"
D4J_PATH="/home/david/Desktop/defects4j/framework/bin"

bug_id=1
project="Time"
command="checkout_bug"
work_dir="$TMP_DIR/$project-$bug_id/"
d4j_path="$D4J_PATH"

cd frameworks
bash defects4j.sh "$command" "$project" "$bug_id" "$work_dir" "$d4j_path"
cd -
```
After running the command above you should see the following console output:
```
Check out program version: Time-1b......................................... OK
```

- Run capr.py
```
$(pwd)/venv/bin/python3 "$(pwd)/main.py"
```
