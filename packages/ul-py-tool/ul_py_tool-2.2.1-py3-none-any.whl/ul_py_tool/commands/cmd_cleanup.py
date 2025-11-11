from ul_py_tool.commands.cmd import Cmd
from ul_py_tool.utils.step import Stepper


class CmdCleanup(Cmd):
    def run(self) -> None:
        stepper = Stepper()

        with stepper.step('fix hooks') as step:
            step.run_cmd('chmod 755 -R .git/hooks')

        with stepper.step('docker login') as step:
            step.run_cmd('docker login gitlab.neroelectronics.by:5050 -u unic-lab-developers -p Fqp99SoNxBYPA8ZPaXy2')

        with stepper.step('git sync') as step:
            step.run_cmd('git submodule init')
            step.run_cmd('git submodule update --remote')

        with stepper.step('pipenv sync') as step:
            step.run_cmd('pipenv sync --dev')
            step.run_cmd('pipenv clean')

        with stepper.step('ulpytool install') as step:
            step.run_cmd('ulpytool install')
