import dataclasses


@dataclasses.dataclass
class PyPackage:
    name: str
    version: str
    new_version: str = ""

    def __str__(self) -> str:
        return f"<{self.name}:{self.version}>"

