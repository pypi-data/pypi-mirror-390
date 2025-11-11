#!/bin/bash
# THIS FILE IS COPYING TO .git/hooks/pre-commit

set -o errexit
set -o pipefail
set -o nounset
cd "$(dirname "${BASH_SOURCE[0]}")"
cd ../../




# RUN
# ======================================================================================================
pipenv run lint
