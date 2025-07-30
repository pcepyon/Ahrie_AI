#!/bin/bash

# Load environment variables from .env file
if [ -f .env ]; then
    set -o allexport
    source .env
    set +o allexport
fi

# Start the application
python3 src/main.py