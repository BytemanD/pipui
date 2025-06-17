import dataclasses
import json
from typing import List

import requests

from pipui.core import executor


@dataclasses.dataclass
class PyPackage:
    name: str
    version: str
    new_version: str = ""

    def __str__(self) -> str:
        return f"<{self.name}:{self.version}>"


class PipManager:

    def __init__(self) -> None:
        self.pip_cmd = executor.Executor("python -m pip")

    def version(self) -> str:
        _, output = self.pip_cmd.execute("--version")
        values = output.strip().split()
        return values[1] if len(values) > 2 else ""

    def last_version(self, name):
        resp = requests.get(f"https://pypi.org/pypi/{name}/json", timeout=60 * 5)
        resp.raise_for_status()
        data = resp.json()
        return data.get("info", {}).get("version")

    def install(self, name, upgrade=False):
        args = ["install"]
        if upgrade:
            args.append("--upgrade")
        args.append(name)
        self.pip_cmd.execute(*args)

    def uninstall(self, name):
        self.pip_cmd.execute("uninstall", "-y", name)

    def config_list(self) -> str:
        _, stdout = self.pip_cmd.execute("config", "list")
        return stdout

    # def config_list(self) -> dict:
    #     _, stdout = self.pip_cmd.execute('config', 'list')
    #     return dict(item.strip().split("=", 1) for item in stdout.split())

    def config_set(self, key, value):
        self.pip_cmd.execute("config", "set", key, value)

    def list_packages(self) -> List[PyPackage]:
        _, stdout = self.pip_cmd.execute("list", "--format", "json")
        return [PyPackage(item.get("name"), item.get("version")) for item in json.loads(stdout)]
