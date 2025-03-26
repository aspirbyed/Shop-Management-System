# Login Page : Fahaad
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QSpacerItem, QSizePolicy, QMessageBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import sys

class LoginForm(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hotel Management System")
        self.resize(550, 500)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Title Label
        self.label_title = QLabel('Login Page')
        self.label_title.setFont(QFont("Arial", 24))
        self.label_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label_title)

        # Username Label and Textbox
        self.label_username = QLabel('Username:')
        self.label_username.setFont(QFont("Arial", 20))
        self.textbox_username = QLineEdit()
        self.textbox_username.setPlaceholderText('Enter your username')
        layout.addWidget(self.label_username)
        layout.addWidget(self.textbox_username)

        # Password Label and Textbox
        self.label_password = QLabel('Password:')
        self.label_password.setFont(QFont("Arial", 20))
        self.textbox_password = QLineEdit()
        self.textbox_password.setPlaceholderText('Enter your password')
        self.textbox_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.label_password)
        layout.addWidget(self.textbox_password)

        # Spacer to push the login button to the bottom
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(spacer)

        # Login Button
        self.button_login = QPushButton('Login')
        self.button_login.setFixedHeight(40)
        self.button_login.clicked.connect(self.check_credentials)
        layout.addWidget(self.button_login)

        self.setLayout(layout)

    def check_credentials(self):
        username = self.textbox_username.text()
        password = self.textbox_password.text()

        if username == 'admin' and password == 'password':
            QMessageBox.information(self, 'Success', 'Login successful!')
        else:
            QMessageBox.warning(self, 'Error', 'Invalid username or password')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    login_form = LoginForm()
    login_form.show()
    sys.exit(app.exec_())