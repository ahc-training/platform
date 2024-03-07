#!/bin/bash

set -e

# Clone the Git repository
git clone -b ${GIT_BRANCH} https://${GIT_USERNAME}:${GIT_TOKEN}@${GIT_REPO} /app/${GIT_TARGET_DIR}

# Set the working directory to the cloned repository
cd /app/${GIT_TARGET_DIR}

# Install project dependencies with Poetry
poetry install

# Activate the Poetry virtual environment
source "$(poetry env info --path)/bin/activate"

# Execute the provided command (spark-submit)
exec "$@"
