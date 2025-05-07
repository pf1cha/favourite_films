# frontend/ui_utils.py
from PyQt6.QtWidgets import QMessageBox


def show_error_message(parent, title, message):
    QMessageBox.critical(parent, title, message)


def show_info_message(parent, title, message):
    QMessageBox.information(parent, title, message)


def show_warning_message(parent, title, message):
    QMessageBox.warning(parent, title, message)
