from urllib import parse

from loguru import logger
from PySide6.QtCore import QThread, Signal

from pipui.core import services
from pipui.ui.widgets import *


class SetPipRepoThread(QThread):
    signal = Signal(str)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.repo = ""

    def set_repo(self, repo: str):
        self.repo = repo

    def run(self):
        result = parse.urlparse(self.repo)
        services.PIP.config_set("global.index-url", self.repo)
        services.PIP.config_set("global.trusted-host", result.hostname)
        logger.debug("set pip repo finished")
        config = services.PIP.config_list()
        self.signal.emit(SignalMessage(success=True, data={'config': config}).to_json())


class GetPipConfigThread(QThread):
    signal = Signal(str)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def run(self):
        config = services.PIP.config_list()
        self.signal.emit(SignalMessage(success=True, data={'config': config}).to_json())


class GetPipVersionThread(QThread):
    signal = Signal(str)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def run(self):
        try:
            version = services.PIP.version()
            self.signal.emit(SignalMessage(success=True, data={'version': version}).to_json())
        except Exception as e:
            self.signal.emit(SignalMessage(success=False, data={}).to_json())


class GetPipLastVersionThread(QThread):
    signal = Signal(str)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def run(self):
        logger.debug("检查pip新版本 ...")
        try:
            version = services.PIP.last_version("pip")
            self.signal.emit(SignalMessage(success=True, data={'version': version}).to_json())
        except Exception as e:
            self.signal.emit(SignalMessage(success=False, data={}).to_json())


class UpdaePipThread(QThread):
    signal = Signal(str)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def run(self):
        logger.debug("更新pip ...")
        try:
            services.PIP.install("pip", upgrade=True)
            logger.debug("更新pip ...")
        except Exception as e:
            self.signal.emit(SignalMessage(success=False, data={}).to_json())
        logger.debug("更新成功")
        try:
           version = services.PIP.version()
           self.signal.emit(SignalMessage(success=True, data={'version': version}).to_json())
        except Exception as e:
            self.signal.emit(SignalMessage(success=False, data={}).to_json())


class CheckPkgVersionThread(QThread):
    signal = Signal(str)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.packages = []

    def set_packages(self, packages: List[PyPackage]):
        self.packages = packages

    def run(self):
        logger.debug("check update start")
        for index, pkg in enumerate(self.packages):
            pkg.new_version = services.PIP.last_version(pkg.name)
            logger.debug("package {} new version: {}", pkg, pkg.new_version)
            data = {"index": index, "name": pkg.name, "new_version": pkg.new_version}
            self.signal.emit(SignalMessage(success=True, data=data).to_json())
        logger.debug("check update finished")


class UninstallPkgThread(QThread):
    signal = Signal(str)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.name = ''

    def set_package(self, name):
        self.name = name

    def run(self):
        if not self.name:
            logger.error("uninstall package name is empty")
            return
        logger.info("start uinstall package {} ...", self.name)
        try:
            services.PIP.uninstall(self.name)
        except Exception as e:
            logger.error("uninstall package {} failed: {}", self.name, e)
            return
        else:
            logger.success("uinstall package {} success", self.name)
            self.signal.emit(SignalMessage(success=True, data={"name": self.name}).to_json())
