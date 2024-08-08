#!/bin/bash

PROJECT_DIR="project"
VENV_DIR="$PROJECT_DIR-venv"

echo "Running post-initialization script as $USER."
echo "Entering $USER's home dir"
cd ~
echo "Creating venv dir for $PROJECT_DIR if it doesn't exist"
mkdir -p $VENV_DIR
echo "Creating venv in $VENV_DIR if it doesn't exist"

if [ ! -f "$VENV_DIR/pyvenv.cfg" ]; then
    echo "No 'pyvenv.cfg' file found in $VENV_DIR; creating a venv"
    python3 -m venv $VENV_DIR
fi

echo "Activating venv in $VENV_DIR"
source $VENV_DIR/bin/activate

echo "Creating dir $PROJECT_DIR if it doesn't exist"
mkdir -p $PROJECT_DIR && cd $PROJECT_DIR

echo "ls printing files"
ls
pwd

cp -r /app .
cd app
echo "ls printing files 2"
ls
pwd

pip install -r requirements.txt

./setup.sh

echo "Running server"
python3 ./recommendation_service/feed_rec_server.py
