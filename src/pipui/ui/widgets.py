import dataclasses
import json
from typing import Callable, List, Optional

from loguru import logger
from PySide6 import QtWidgets
from PySide6.QtWidgets import (QAbstractButton, QComboBox,  # fmt: skip
                               QHBoxLayout, QHeaderView, QLabel, QPushButton,
                               QTableWidget, QTableWidgetItem, QVBoxLayout,
                               QWidget)

from pipui.core.manager.pip import PyPackage


@dataclasses.dataclass
class SignalMessage:
    success: bool
    data: dict = dataclasses.field(default_factory=dict)

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, data) -> 'SignalMessage':
        msg = json.loads(data)
        return cls(success=msg.get('success', False), data=msg.get("data", {}))


def v_h3(text):
    label = QLabel(text)
    label.setStyleSheet("font-size: 24px; font-weight: bold;")
    return label


def v_h4(text):
    label = QLabel(text)
    label.setStyleSheet("font-size: 20px; font-weight: bold")
    return label


def v_h5(text):
    label = QLabel(text)
    label.setStyleSheet("font-size: 15px; font-weight: bold;")
    return label


def v_button(text, color=None, onclick: Optional[Callable] = None,
             variant=None, disabled=False) -> QPushButton:
    btn = QPushButton(text)
    if color:
        btn.setProperty("class", color)
    if variant:
        btn.setProperty("name", variant)
    if onclick:
        btn.clicked.connect(onclick)
    if disabled:
        btn.setDisabled(disabled)
    return btn


def v_button_group(buttons: List[QAbstractButton]) -> QWidget:
    group = QtWidgets.QButtonGroup()
    for btn in buttons:
        group.addButton(btn)
    return v_row(buttons)  # type: ignore


def v_row(children: List[QWidget]) -> QWidget:
    layout = QHBoxLayout()
    widget = QWidget()
    widget.setLayout(layout)
    for child in children:
        layout.addWidget(child)
    layout.addStretch()
    return widget


def v_column(children: List[QWidget]) -> QWidget:
    layout = QVBoxLayout()
    widget = QWidget()
    widget.setLayout(layout)
    for child in children:
        layout.addWidget(child)
    layout.addStretch()
    return widget


def v_dropdown_selector(items: List[str], min_width=None) -> QComboBox:
    box = QComboBox()
    if min_width:
        box.setMinimumWidth(min_width)
    box.addItems(items)
    return box


class VLabel(QWidget):

    def __init__(self, title: str, *args, subtitle: str = "", **kwargs):
        super().__init__(*args, **kwargs)
        self._layout = QHBoxLayout()
        self._layout.setContentsMargins(5, 2, 5, 2)
        self._layout.setSpacing(5)
        self.setLayout(self._layout)
        self._layout.addWidget(QLabel(title))

        self._layout.addWidget(QLabel(subtitle))
        # self._layout.addWidget(self.icon)


class PackageTable(QWidget):
    def __init__(self, header: List[str], *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.table = QTableWidget()
        self.table.setColumnCount(len(header) + 1)
        self.table.setHorizontalHeaderLabels(header + ["操作"])

        table_header = self.table.horizontalHeader()
        assert table_header is not None
        table_header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self._layout = QHBoxLayout()
        self._layout.addWidget(self.table)
        self.setLayout(self._layout)

    def set_packages(self, packaes: List[PyPackage]):
        self.table.clearContents()
        self.table.setRowCount(len(packaes))
        for index, package in enumerate(packaes):
            self.table.setItem(index, 0, QTableWidgetItem(package.name))
            self.table.setItem(index, 1, QTableWidgetItem(package.version))
            self.table.setItem(index, 2, QTableWidgetItem(package.new_version or "-"))

            widget = QWidget()
            layout = QHBoxLayout(widget)
            layout.setContentsMargins(0, 0, 0, 0)

            btn2 = v_button(
                "更新", color="warning", variant="checked",
                onclick=lambda _, p=package: self.update_package(p)
            )
            btn1 = v_button(
                "卸载", color="danger", variant="text",
                onclick=lambda _, p=package: self.uninstall_package(p)
            )

            layout.addWidget(btn1)
            layout.addWidget(btn2)
            layout.addStretch()

            self.table.setCellWidget(index, 3, widget)

    def update_item(self, msg: str):
        data = SignalMessage.from_json(msg).data
        item = self.table.item(data.get('index', 0), 2)
        if item:
            logger.debug("update package {}({}) new_version {}",
                         msg.index, data.get('name', ''), data['new_version'])
            item.setText(data['new_version'])

    def update_package(self, package: PyPackage):
        logger.debug("uninstall package {}", package)

    def uninstall_package(self, package: PyPackage):
        logger.debug("update package {}", package)
