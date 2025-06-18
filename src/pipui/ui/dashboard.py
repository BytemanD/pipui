import sys

from loguru import logger
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QHBoxLayout, QLabel, QListWidget,  # fmt: skip
                               QListWidgetItem, QMainWindow, QMessageBox,
                               QStackedWidget, QVBoxLayout, QWidget)

from . import pages


def excepthook(exc_type, exc_value, exc_traceback):
    """全局异常处理"""
    logger.exception(
        exc_value,
    )

    QMessageBox.critical(None, "未处理的异常", f"{exc_type}:\n{exc_value}")


sys.excepthook = excepthook


class Dashboard(QMainWindow):

    def __init__(self, title=None) -> None:
        super().__init__()
        self.setGeometry(100, 100, 1000, 800)
        self.setWindowTitle(title or "Dashboard")
        self.main_layout = QHBoxLayout()

        # 主窗口部件 - 水平布局
        self.setCentralWidget(QWidget())
        if mian_widget := self.centralWidget():
            mian_widget.setLayout(self.main_layout)

        # 导航栏容器 - 垂直布局
        self.left_nav = QWidget()
        self.nav_layout = QVBoxLayout()
        self.left_nav.setFixedWidth(200)
        self.left_nav.setLayout(self.nav_layout)
        self.left_nav.setStyleSheet(
            """
            background-color: #2c3e50;
            color: white;
            font-size: 14px;
        """
        )

        # 右侧容器 & 布局
        # 使用堆叠窗口实现页面切换
        self.stacked_pages = QStackedWidget()
        self.right_layout = QVBoxLayout()
        self.right_layout.addWidget(self.stacked_pages)
        self.right_content = QWidget()
        self.right_content.setLayout(self.right_layout)

        self.main_layout.addWidget(self.left_nav)
        self.main_layout.addWidget(self.right_content)

    def _left_nav_add(self, widge):
        self.nav_layout.addWidget(widge)

    def create_left_navigation(self):
        """创建左侧导航栏"""
        title_label = QLabel("PipManager")
        # self.title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(
            """
            font-size: 18px;
            font-weight: bold;
            padding: 20px 0;
            border-bottom: 1px solid #34495e;
        """
        )
        self._left_nav_add(title_label)

        # 导航列表
        self.nav_list = QListWidget()
        self.nav_list.setStyleSheet(
            """
            QListWidget::item {
                color: white;
                padding-left: 20px;
            }
        """
        )

        # 添加导航项
        nav_items = [
            {"text": "包管理", "icon": "users"},
            {"text": "配置", "icon": "chart"},
            {"text": "关于", "icon": "home"},
        ]

        for item in nav_items:
            list_item = QListWidgetItem(QIcon(f":/icons/{item['icon']}.png"), item["text"])
            self.nav_list.addItem(list_item)
        self._left_nav_add(self.nav_list)

        # 底部空白填充
        # self.nav_layout.addStretch()

    def create_right_content(self):
        """创建右侧内容区域"""
        # 创建各页面
        self.stacked_pages.addWidget(pages.PipPackages())
        self.stacked_pages.addWidget(pages.PipConfig())
        self.stacked_pages.addWidget(pages.PipVersion())

    def show(self):
        # 左侧导航栏
        self.create_left_navigation()
        # 右侧内容区域
        self.create_right_content()

        # 连接信号槽
        def change_page(index):
            """切换页面"""
            self.stacked_pages.setCurrentIndex(index)

        self.nav_list.currentRowChanged.connect(change_page)

        # 默认显示第一页
        self.nav_list.setCurrentRow(0)

        super().show()
