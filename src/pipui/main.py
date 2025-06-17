import sys

from PySide6 import QtWidgets
from qt_material import apply_stylesheet

from pipui.common import logging
from pipui.ui import dashboard


def show_dashboard():
    app = QtWidgets.QApplication(sys.argv)
    apply_stylesheet(app, theme="light_blue.xml", invert_secondary=True)

    window = dashboard.Dashboard(title="PipManager")
    window.show()
    app.exec()


def main():
    logging.setup_logger()
    show_dashboard()


if __name__ == "__main__":
    main()
