#!/bin/bash

TASK_KEY="$1"
SESSION_DIR="$(pwd)/c_sessions/user_${TASK_KEY}_session"

cleanup() {
    # rm -rf "$SESSION_DIR"
    echo meow > "meow.txt"
}

trap cleanup EXIT
trap 'exit 143' TERM
trap 'exit 130' INT

mkdir -p "$SESSION_DIR"

# Preserve submitted code exactly
cat > "$SESSION_DIR/main.c"

docker run \
    --rm \
    --network none \
    --memory 1024m \
    --cpus 0.5 \
    --pids-limit 32 \
    --cap-drop ALL \
    --security-opt no-new-privileges \
    --user 65534:65534 \
    --tmpfs /work:rw,exec,nosuid,nodev,size=64m,mode=1777 \
    -v "$SESSION_DIR:/input:ro" \
    -w /work \
    gcc:14 \
    sh -c '
        gcc /input/main.c -o /work/main 2> /work/compile_errors.txt

        if [ $? -ne 0 ]; then
            echo "FAILED TO COMPILE:"
            cat /work/compile_errors.txt
            exit 1
        fi

        timeout 10s /work/main
    '