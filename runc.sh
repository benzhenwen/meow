#!/bin/bash

TASK_KEY=$1
CODE_INPUT=$(cat)

cd c_sessions
mkdir "user_${TASK_KEY}_session"
cd "user_${TASK_KEY}_session"

echo $CODE_INPUT > main.c
gcc main.c -o main > output_compile.txt

if [ $? -eq 0 ]; then
    ./main
else
    echo "FAILED TO COMPILE:"
    echo output_compile.txt

cd ..
rm -rf "user_${TASK_KEY}_session"