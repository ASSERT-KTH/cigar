# Conversational Automated Program Repair


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

- Run capr.py
```
./venv/bin/python3 "$(pwd)/main.py"
```

## Tasks

- [ ] Reproduce the process and results of [this](https://docs.gitlab.com/ee/user/project/repository/web_editor.html#upload-a-file) paper
