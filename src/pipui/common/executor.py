import subprocess

from loguru import logger


class Executor:

    def __init__(self, cmd) -> None:
        self.cmd = cmd

    def execute(self, *args):
        cmd = [self.cmd]
        cmd.extend(args)
        logger.debug("RUN: {}", " ".join(cmd))
        status, output = subprocess.getstatusoutput(
            " ".join(cmd),
        )
        logger.debug("Return: [{}], output:\n{}", status, output)
        if status != 0:
            raise subprocess.CalledProcessError(status, output)
        return status, output
