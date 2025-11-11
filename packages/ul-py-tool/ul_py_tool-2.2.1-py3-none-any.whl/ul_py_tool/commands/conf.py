import os

MAX_LINE_LEN = 180
INDENT_SIZE = 4

THIS_LIB_PATH = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

PYENV_PY_VERSION = '.python-version'

MYPY_CONFIG = 'mypy.ini'

PY_TYPED = 'py.typed'

PIPFILE = 'Pipfile'
PIPFILE_LOCK = 'Pipfile.lock'

SOURCE_PYPI = 'pypi'
SOURCE_NERO_GITLAB = 'nero_gitlab'

GITLAB_TOKEN = 'KSnT_2NZ_cstDqvLmg-k'

SOURCE_NERO_GITLAB_HOST = 'gitlab.neroelectronics.by'
SOURCE_NERO_GITLAB_URL = f'https://__token__:{GITLAB_TOKEN}@gitlab.neroelectronics.by/api/v4/projects/996/packages/pypi/simple'

# curl --header "PRIVATE-TOKEN: KSnT_2NZ_cstDqvLmg-k" "https://gitlab.neroelectronics.by/api/v4/projects/527/registry/repositories"

HELM_ERROR__NOT_FOUND = 'No results found'
KUEBERNETES_SLEEP_TIME = 60

CHANGE_LOG = 'CHANGELOG.md'
SERVICE_CHANGE_LOG = 'SERVICE_CHANGELOG.md'

SUPPORTED_PYTHON_VERSIONS = {'3.8', '3.10'}

PRE_PUSH_DEST = os.path.join(os.getcwd(), ".git", "hooks", "pre-push")
PRE_COMMIT_DEST = os.path.join(os.getcwd(), ".git", "hooks", "pre-commit")

UNDER_DOCKER = os.path.exists('/docker_app')

UNDER_CI_JOB = bool(os.environ.get('CI_JOB_ID')) and bool(os.environ.get('CI_COMMIT_SHA')) and bool(os.environ.get('CI_REPOSITORY_URL'))
