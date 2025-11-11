# ul-py-tool
> This library allows to bootstrap Python UnicLab project from scratch.
> It provides a set of useful CMD commands mapping in *main.py* file.

```python
def main() -> None:
    Cmd.main({
        'code_stats': 'ul_py_tool.commands.cmd_stats:CmdStats',
        'minor': 'ul_py_tool.commands.cmd_version:CmdVersionMinor',
        'major': 'ul_py_tool.commands.cmd_version:CmdVersionMajor',
        'patch': 'ul_py_tool.commands.cmd_version:CmdVersionPatch',
        'lint': 'ul_py_tool.commands.cmd_lint:CmdLint',
        'install': 'ul_py_tool.commands.cmd_install:CmdInstall',
        'test': 'ul_py_tool.commands.cmd_test:CmdTest',
        'fmt': 'ul_py_tool.commands.cmd_fmt:CmdFmt',
        'release': 'ul_py_tool.commands.cmd_release:CmdRelease',
        'test_secrets': 'ul_py_tool.commands.cmd_test_secrets.py:CmdTestSecrets',
        'build-images': 'ul_py_tool.commands.cmd_build_images:CmdBuildImages',
        'outdated': 'ul_py_tool.commands.cmp_outdated:CmdOutdated',
        'cleanup': 'ul_py_tool.commands.cmd_cleanup:CmdCleanup',
        'fix_own': 'ul_py_tool.commands.cmd_fix_own:CmdFixOwn',
    })
```

> This maps the code of the CMD command to its name. After mapping, we can use a command like this:
```bash
python -m FOLDER_NAME_WHERE_MAIN_PY_LOCATED command_name
python -m src run_some_script  # main.py located in src/ root
```


| Command        | Desription                                                                     |
|----------------|--------------------------------------------------------------------------------|
| Cmd            | Base class. Each command should inherit from it and provide method *run()*.    |
| CmdStats       | Command that provides us statistics about service, lines of code written, etc. |
| CmdVersion     | Command that applies a versioning to setup.py (major, minor, patch).           |
| CmdTest        | Command that runs tests.                                                       |
| CmdRelease     | Command for making a release.                                                  |
| CmdLint        | Command to run lint (different steps).                                         |
| CmdFmt         | Command to apply formatting (black, isort (to be implemented)).                |
| CmdBuildImages | Command that helps to build & push to the registry Docker images.              |
| CmdInstall     | Generates project files, configs, pre-commits, etc.                            |

