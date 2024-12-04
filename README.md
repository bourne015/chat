# Chat
A Fastapi service wrappered ChatGPT API

## Deploy

### 1. create && activate venv
`python3 -m venv .venv`

`source .venv/bin/activate`

### 2. install dependencies
`python3 -m pip install requirements.txt`

### 3. deploy db
* install postgresql

    `sudo apt-get install postgresql postgresql-client`

* create db

    ...

* config

    `alembic upgrade head`

### 4. config OSS(optional)
...

## Run
`python3 main.py`
