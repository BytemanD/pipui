
from loguru import logger
from PySide6.QtWidgets import QLabel, QPlainTextEdit, QVBoxLayout, QWidget

from pipui.core import services
from pipui.ui import threads
from pipui.ui.widgets import *

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

        layout = QVBoxLayout()
        self.setLayout(layout)

        self._thead_get_pip_version = threads.GetPipVersionThread()
        self._thead_get_pip_version.signal.connect(self._refresh_pip_version)

        self._thead_get_pip_last_version = threads.GetPipLastVersionThread()
        self._thead_get_pip_last_version.signal.connect(self._refresh_pip_last_version)

        self._thead_update_pip = threads.UpdaePipThread()
        self._thead_update_pip.signal.connect(self._refresh_pip_version)

        self.btn_upgrade = v_button("更新", color="success", disabled=True,
                                    onclick=self._thead_update_pip.start)
        for child in [
            self.label_version,
            self.label_new_version,
            v_button_group(
                [
                    v_button("卸载", color="danger", onclick=self._uninstall_pip),
                    v_button("检测更新 ...", color="info", onclick=self._get_pip_last_version),
                    self.btn_upgrade,
                ]
            ),
        ]:
            layout.addWidget(child)
        layout.addStretch()

        self._get_pip_version()

    def _get_pip_version(self):
        self._thead_get_pip_version.start()

    def _refresh_pip_version(self, msg: str):
        signal_msg = SignalMessage.from_json(msg)
        if signal_msg.success:
            self.pip_version = signal_msg.data.get('version', '')
            self.label_version.setText(f"pip版本: {self.pip_version}")
        else:
            self.label_version.setText("未安装")
        self.btn_upgrade.setDisabled(True)

    def _get_pip_last_version(self):
        self._thead_get_pip_last_version.start()

    def _refresh_pip_last_version(self, msg: str):
        signal_msg = SignalMessage.from_json(msg)
        if signal_msg.success:
            new_version = signal_msg.data.get('version', '')
            if new_version != self.pip_version:
                label = f"🎉新版本: {new_version}"
                self.btn_upgrade.setDisabled(False)
            else:
                label = "无可用更新"
                self.btn_upgrade.setDisabled(True)
        else:
            label = "❗检查失败"
            self.btn_upgrade.setDisabled(False)
        self.label_new_version.setText(label)
        

    def _uninstall_pip(self, *args):
        raise ImportError("uninstall pip")



class PipConfig(QWidget):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.text_config = QPlainTextEdit()
        self.text_config.setReadOnly(True)
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
            v_row([
                v_h5("选择源:"),
                self.box_pip_repos,
                v_button("设置", color="info", onclick=self._set_pip_repo),
            ]),
        ]:
            layout.addWidget(child)
        layout.addStretch()

        self._thead_get_pip_config = threads.GetPipConfigThread()
        self._thead_get_pip_config.signal.connect(self._refresh_pip_config)
        self._thead_set_pip_repo = threads.SetPipRepoThread()
        self._thead_set_pip_repo.signal.connect(self._refresh_pip_config)

        self._init_data()

    def _init_data(self):
        self._thead_get_pip_config.start()

    def _refresh_pip_config(self, msg: str):
        config = SignalMessage.from_json(msg).data.get('config', '')
        self.text_config.setPlainText(config)

    def _set_pip_repo(self):
        repo_name = self.box_pip_repos.currentText()
        repo = PIP_REPOS.get(repo_name)
        if not repo:
            return
        logger.debug("set pip repo -> {}({})", repo_name, repo)
        self._thead_set_pip_repo.set_repo(repo)
        self._thead_set_pip_repo.start()


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

        self.update_progress = v_progress_bar(hide=True)

        for child in [
            v_row([
                v_button_group([self.btn_check_version]),
                self.update_progress,
            ]),
            self.table,
        ]:
            layout.addWidget(child)

        self._refresh_pip_packages()
        self._thread = threads.CheckPkgVersionThread()
        self._thread.signal.connect(self._receive_update_signal)

    def _refresh_all_version(self):
        logger.debug("start update thread", self._thread)
        self._show_and_reset_progress()
        self._thread.set_packages(self.packages)
        self._thread.start()

    def _receive_update_signal(self, msg: str):
        self.table.update_item(msg)
        self.update_progress.setValue(self.update_progress.value() + 1)
        logger.debug("completed: {}", self.update_progress.value())

    def _show_and_reset_progress(self):
        self.update_progress.setHidden(False)
        self.update_progress.setValue(0)
        self.update_progress.setRange(0, len(self.packages))

    def _refresh_pip_packages(self):
        self.packages = services.PIP.list_packages()
        self.table.set_packages(self.packages)
