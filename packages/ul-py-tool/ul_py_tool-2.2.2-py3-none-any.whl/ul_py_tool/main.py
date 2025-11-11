import os.path
import sys

if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from ul_py_tool.commands.cmd import Cmd


def main() -> None:
    Cmd.main({
        'code_stats': 'ul_py_tool.commands.cmd_stats:CmdStats',
        'service_minor': 'ul_py_tool.commands.cmd_service_version:CmdServiceVersionMinor',
        'service_major': 'ul_py_tool.commands.cmd_service_version:CmdServiceVersionMajor',
        'service_patch': 'ul_py_tool.commands.cmd_service_version:CmdServiceVersionPatch',
        'minor': 'ul_py_tool.commands.cmd_version:CmdVersionMinor',
        'major': 'ul_py_tool.commands.cmd_version:CmdVersionMajor',
        'patch': 'ul_py_tool.commands.cmd_version:CmdVersionPatch',
        'lint': 'ul_py_tool.commands.cmd_lint:CmdLint',
        'install': 'ul_py_tool.commands.cmd_install:CmdInstall',
        'test': 'ul_py_tool.commands.cmd_test:CmdTest',
        'fmt': 'ul_py_tool.commands.cmd_fmt:CmdFmt',
        'release': 'ul_py_tool.commands.cmd_release:CmdRelease',
        'release-dcf': 'ul_py_tool.commands.cmd_release_dcf:CmdReleaseDcf',
        'release-dcf-dev': 'ul_py_tool.commands.cmd_release_dcf_dev:CmdReleaseDcfDev',
        'test_secrets': 'ul_py_tool.commands.cmd_test_secrets:CmdTestSecrets',
        'build-images': 'ul_py_tool.commands.cmd_build_images:CmdBuildImages',
        'outdated': 'ul_py_tool.commands.cmp_outdated:CmdOutdated',
        'cleanup': 'ul_py_tool.commands.cmd_cleanup:CmdCleanup',
        'fix_own': 'ul_py_tool.commands.cmd_fix_own:CmdFixOwn',
        'render_values': 'ul_py_tool.commands.cmd_render_values:CmdRenderValues',
    })


if __name__ == '__main__':
    main()
