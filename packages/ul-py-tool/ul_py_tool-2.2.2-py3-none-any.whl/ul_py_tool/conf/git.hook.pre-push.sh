#!/bin/bash
# THIS FILE IS COPYING TO .git/hooks/pre-push

set -o errexit
set -o pipefail
set -o nounset
cd "$(dirname "${BASH_SOURCE[0]}")"
cd ../../




# RUN
# ======================================================================================================
pipenv run lint
pipenv run test
