from ul_py_tool.commands.cmd import Cmd
from ul_py_tool.utils.step import Stepper


class CmdFixOwn(Cmd):

    def run(self) -> None:
        stepper = Stepper()

        with stepper.step('fix') as stp:
            stp.run_cmd('sudo chown $(whoami):$(whoami) -R .')
