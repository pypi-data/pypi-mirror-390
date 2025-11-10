#!/bin/bash

# Load environment variables from .env
if [ -f .env ]; then
    export $(cat .env | xargs)
fi

# Run uv publish with the loaded token
uv publish "$@"