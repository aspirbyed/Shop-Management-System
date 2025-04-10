from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QSpacerItem, QSizePolicy, QMessageBox, QHBoxLayout
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from PyQt5.QtSql import QSqlDatabase
from PyQt5.QtSql import QSqlDatabase, QSqlQuery

from dashboard import MainWindow

import sys
import os
import shutil
import logging

# Helper function to locate resources
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# Helper function to get a writable database path
def get_writable_db_path():
    # Use the directory of the executable as the base path for writable files
    base_path = os.path.dirname(sys.executable)
    writable_db_path = os.path.join(base_path, "sms.db")
    
    # If the writable database doesn't exist, copy it from the bundled location
    if not os.path.exists(writable_db_path):
        try:
            original_db_path = resource_path("sms.db")
            shutil.copy2(original_db_path, writable_db_path)
            logging.info(f"Copied sms.db from {original_db_path} to {writable_db_path}")
        except Exception as e:
            logging.error(f"Failed to copy sms.db: {str(e)}")
            return None
    return writable_db_path

# Redirect console output to a log file
# base_path = os.path.dirname(sys.executable)
# log_file = os.path.join(base_path, "sms.log")
# logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# class LoggerWriter:
#     def __init__(self, logger, level):
#         self.logger = logger
#         self.level = level

#     def write(self, message):
#         if message.strip():
#             self.logger.log(self.level, message.strip())

#     def flush(self):
#         pass

# sys.stdout = LoggerWriter(logging.getLogger(), logging.INFO)
# sys.stderr = LoggerWriter(logging.getLogger(), logging.ERROR)

class LoginForm(QWidget):
    def __init__(self):
        super().__init__()
        self.main_window = None  # Reference to MainWindow
        self.setWindowTitle("Shop Management System")
        self.setGeometry(100, 100, 800, 600)
        self.setup_ui()

    def setup_ui(self):
        # Main vertical layout for centering
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)

        # Inner vertical layout for form elements
        form_layout = QVBoxLayout()

        # Title
        self.label_title = QLabel('Login Page')
        self.label_title.setFont(QFont("Arial", 24))
        self.label_title.setAlignment(Qt.AlignCenter)
        # form_layout.addWidget(self.label_title)

        # Username Field
        self.label_username = QLabel('Username:')
        self.label_username.setFont(QFont("Arial", 16))
        self.textbox_username = QLineEdit()
        self.textbox_username.setPlaceholderText('Enter your username')
        self.textbox_username.setStyleSheet('padding: 5px;')
        form_layout.addWidget(self.label_username)
        form_layout.addWidget(self.textbox_username)

        # Password Field
        self.label_password = QLabel('Password:')
        self.label_password.setFont(QFont("Arial", 16))
        self.textbox_password = QLineEdit()
        self.textbox_password.setPlaceholderText('Enter your password')
        self.textbox_password.setEchoMode(QLineEdit.Password)
        self.textbox_password.setStyleSheet('padding: 5px;')
        form_layout.addWidget(self.label_password)
        form_layout.addWidget(self.textbox_password)

        # Spacer for better positioning
        form_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Login Button (Bigger)
        self.button_login = QPushButton('Login')
        self.button_login.setMinimumSize(250, 50)
        self.button_login.clicked.connect(self.check_credentials)
        form_layout.addWidget(self.button_login, alignment=Qt.AlignCenter)

        # Add stretchers for vertical centering
        main_layout.addStretch()
        main_layout.addWidget(self.label_title)
        main_layout.addLayout(form_layout)
        main_layout.addStretch()

        # Wrap inside an HBox for horizontal centering
        wrapper_layout = QHBoxLayout()
        wrapper_layout.addStretch()
        wrapper_layout.addLayout(main_layout)
        wrapper_layout.addStretch()

        self.setLayout(wrapper_layout)

    def check_credentials(self):
        username = self.textbox_username.text()
        password = self.textbox_password.text()

        if username == 'admin' and password == 'password':
            # QMessageBox.information(self, 'Success', 'Login successful!')
            self.hide()  # Hide instead of close
            if not self.main_window:
                self.main_window = MainWindow(self)  # Pass self as parent
            self.main_window.show()
        else:
            QMessageBox.warning(self, 'Error', 'Invalid username or password')

    def reset(self):
        """Reset form for next login attempt"""
        self.textbox_username.clear()
        self.textbox_password.clear()
        self.show()

if __name__ == '__main__':
    # db_path = get_writable_db_path()
    # if db_path is None:
    #     QMessageBox.critical(None, "Error", "Could not copy database file")
    #     sys.exit(1)
    database = QSqlDatabase.addDatabase("QSQLITE")
    database.setDatabaseName("sms.db")

    if not database.open():
        QMessageBox.critical(None, "Database Error", "Could not open database")
        sys.exit(1)

    query = QSqlQuery()
    if not query.exec("PRAGMA foreign_keys = ON;"):
        QMessageBox.critical(None, "Database Error", "Error enabling foreign keys:")
        sys.exit(1)

    app = QApplication(sys.argv)
    window = LoginForm()
    window.show()
    
    exit_code = app.exec_()

    database.close()
    QSqlDatabase.removeDatabase("qt_sql_default_connection")

    sys.exit(exit_code)
