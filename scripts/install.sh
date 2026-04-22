#!/usr/bin/env bash
# Thin wrapper around install.py so users can call install.sh directly.
# Usage: ./install.sh <project-path> [target ...]
set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
exec python "$DIR/install.py" "$@"
