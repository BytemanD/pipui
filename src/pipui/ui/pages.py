from urllib import parse

import pip
from loguru import logger
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QLabel, QPlainTextEdit, QVBoxLayout, QWidget

from pipui.core import pip
from pipui.ui.widgets import *

PIP_MANATER = pip.PipManager()

PIP_REPOS = {
    "官方": "https://pypi.org/simple",
    "清华大学": "https://pypi.tuna.tsinghua.edu.cn/simple",
    "中国科技大学": "https://pypi.mirrors.ustc.edu.cn/simple",
    "阿里云": "https://mirrors.aliyun.com/pypi/simple",
    "腾讯": "http://mirrors.cloud.tencent.com/pypi/simple",
}


class PipVersion(QWidget):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.pip_version = ""
        self.label_version = v_h4("")
        self.label_new_version = QLabel("-")
        self.btn_upgrade = v_button(
            "更新", color="success", disabled=True, onclick=self._upgrade_pip
        )

        layout = QVBoxLayout()
        self.setLayout(layout)
        for child in [
            self.label_version,
            self.label_new_version,
            v_button_group(
                [
                    v_button("卸载", color="danger", onclick=self._uninstall_pip),
                    v_button("检测更新 ...", color="info", onclick=self._refresh_new_version),
                    self.btn_upgrade,
                ]
            ),
        ]:
            layout.addWidget(child)
        layout.addStretch()
        self._refresh_pip_version()
        # self._refresh_new_version()s

    def _upgrade_pip(self):
        pip_version = PIP_MANATER.version()
        PIP_MANATER.install("pip", upgrade=True)
        new_version = PIP_MANATER.version()
        if new_version == pip_version:
            logger.warning("无可用更新")
        else:
            logger.success("更新成功 {} -> {}", pip_version, new_version)
            self.label_version.setText(f"pip版本: {new_version}")
            self.label_new_version.setText("")
            self.btn_upgrade.setDisabled(True)

    def _uninstall_pip(self, *args):
        raise ImportError("uninstall pip")

    def _refresh_new_version(self):
        logger.debug("检查新版本 ...")
        self.btn_upgrade.setDisabled(True)
        new_version = PIP_MANATER.last_version("pip")
        if new_version == self.pip_version:
            logger.debug("无可用更新 ...")
            self.label_new_version.setText("无可用更新")
            self.btn_upgrade.setDisabled(True)
        else:
            self.label_new_version.setText(f"🎉新版本: {new_version}")
            self.btn_upgrade.setDisabled(False)

    def _refresh_pip_version(self):
        self.pip_version = PIP_MANATER.version()
        self.label_version.setText(f"版本: {self.pip_version}" if self.pip_version else "未安装")


class PipConfig(QWidget):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.text_config = QPlainTextEdit()
        # self.text_config.setDisabled(True)
        self.text_config.setMaximumBlockCount(10)
        font = self.text_config.font()
        font.setFamily("Courier New")
        self.text_config.setFont(font)

        self.box_pip_repos = v_dropdown_selector(list(PIP_REPOS.keys()), min_width=150)
        self.box_pip_repos.currentText()

        layout = QVBoxLayout()
        self.setLayout(layout)
        for child in [
            v_h4("配置"),
            self.text_config,
            v_row(
                [
                    v_h5("选择源:"),
                    self.box_pip_repos,
                    v_button("设置", color="info", onclick=self._set_pip_repo),
                ]
            ),
        ]:
            layout.addWidget(child)
        layout.addStretch()

        self._refresh_pip_config()

    def _refresh_pip_config(self):
        config = PIP_MANATER.config_list()
        self.text_config.setPlainText(config)

    def _set_pip_repo(self):
        repo_name = self.box_pip_repos.currentText()
        repo = PIP_REPOS.get(repo_name)
        logger.debug("set pip repo -> {}({})", repo_name, repo)
        result = parse.urlparse(repo)
        PIP_MANATER.config_set("global.index-url", repo)
        PIP_MANATER.config_set("global.trusted-host", result.hostname)
        self._refresh_pip_config()


class CheckPkgVersionThread(QThread):
    update_signal = pyqtSignal(str)

    def set_packages(self, packages: List[PyPackage]):
        self.packages = packages

    def run(self):
        import json

        logger.debug("check update start")
        for index, pkg in enumerate(self.packages):
            pkg.new_version = PIP_MANATER.last_version(pkg.name)
            logger.debug("package {} new version: {}", pkg, pkg.new_version)
            self.update_signal.emit(
                json.dumps({"index": index, "name": pkg.name, "new_version": pkg.new_version})
            )
        logger.debug("check update finished")


class PipPackages(QWidget):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.table = PackageTable(["包名", "版本", "新版本"])
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.packages: List[PyPackage] = []

        self.btn_check_version = v_button(
            "检测更新...", color="info", onclick=self._refresh_all_version
        )

        for child in [
            v_button_group([self.btn_check_version]),
            self.table,
        ]:
            layout.addWidget(child)

        self._refresh_pip_packages()
        self._thread = CheckPkgVersionThread()
        self._thread.update_signal.connect(self.table.update_item)

    def _refresh_all_version(self):
        self._thread.set_packages(self.packages)
        logger.debug("start update thread", self._thread)
        self._thread.start()

    def _refresh_pip_packages(self):
        self.packages = PIP_MANATER.list_packages()
        self.table.set_packages(self.packages)
