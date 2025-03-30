from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QGridLayout, QLabel, QVBoxLayout,
    QMainWindow, QStackedWidget, QTableWidget, QMessageBox, QTableWidgetItem,
    QDialog, QFormLayout, QLineEdit, QHBoxLayout, QScrollArea, QComboBox
)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlError
import sys

# Import the page classes
from billing import BillingPage
from discount import DiscountPage
from report import ReportPage
from stocks import StockPage
from category import CategoryPage
from products import ProductPage
from supplier import SuppliersPage

class MainPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        # Create navigation buttons
        self.billing_btn = QPushButton("Billing Page")
        self.discount_btn = QPushButton("Discount Page")
        self.category_btn = QPushButton("Category Page")
        self.products_btn = QPushButton("Products Page")
        self.stocks_btn = QPushButton("Stocks Page")
        self.suppliers_btn = QPushButton("Suppliers Page")
        self.report_btn = QPushButton("Report Page")
        self.logout_btn = QPushButton("Logout")

        # Add buttons to the layout
        layout.addWidget(self.billing_btn)
        layout.addWidget(self.discount_btn)
        layout.addWidget(self.category_btn)
        layout.addWidget(self.products_btn)
        layout.addWidget(self.stocks_btn)
        layout.addWidget(self.suppliers_btn)
        layout.addWidget(self.report_btn)
        layout.addWidget(self.logout_btn)
        layout.addStretch()

class MainWindow(QMainWindow):
    def __init__(self, login_form=None):
        super().__init__()
        self.login_form = login_form  # Store reference to login form
        self.setWindowTitle("Shop Management System")
        self.setGeometry(100, 100, 800, 600)

        # Create the stacked widget for page switching
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Create the main page
        self.main_page = MainPage()

        # Create instances of other pages
        self.billing_page = BillingPage(self)
        self.discount_page = DiscountPage(self)
        self.category_page = CategoryPage(self)
        self.products_page = ProductPage(self)
        self.stocks_page = StockPage(self)
        self.suppliers_page = SuppliersPage(self)
        self.report_page = ReportPage(self)

        # Add all pages to the stacked widget
        self.stack.addWidget(self.main_page)
        self.stack.addWidget(self.billing_page)
        self.stack.addWidget(self.discount_page)
        self.stack.addWidget(self.category_page)
        self.stack.addWidget(self.products_page)
        self.stack.addWidget(self.stocks_page)
        self.stack.addWidget(self.suppliers_page)
        self.stack.addWidget(self.report_page)

        # Connect main page buttons to navigation functions
        self.main_page.billing_btn.clicked.connect(self.show_billing)
        self.main_page.discount_btn.clicked.connect(self.show_discount)
        self.main_page.category_btn.clicked.connect(self.show_category)
        self.main_page.products_btn.clicked.connect(self.show_products)
        self.main_page.stocks_btn.clicked.connect(self.show_stocks)
        self.main_page.suppliers_btn.clicked.connect(self.show_suppliers)
        self.main_page.report_btn.clicked.connect(self.show_report)
        self.main_page.logout_btn.clicked.connect(self.logout)

        # Set the initial page to the main page
        self.stack.setCurrentWidget(self.main_page)

    def show_billing(self):
        self.stack.setCurrentWidget(self.billing_page)

    def show_products(self):
        self.stack.setCurrentWidget(self.products_page)

    def show_stocks(self):
        self.stack.setCurrentWidget(self.stocks_page)

    def show_report(self):
        self.stack.setCurrentWidget(self.report_page)

    def show_discount(self):
        self.stack.setCurrentWidget(self.discount_page)

    def show_suppliers(self):
        self.stack.setCurrentWidget(self.suppliers_page)

    def show_category(self):
        self.stack.setCurrentWidget(self.category_page)

    def show_main(self):
        self.stack.setCurrentWidget(self.main_page)

    def logout(self):
        """Handle logout functionality"""
        self.hide()  # Hide dashboard
        if self.login_form:
            self.login_form.reset()  # Show and reset login form

# database = QSqlDatabase.addDatabase("QSQLITE")
# database.setDatabaseName("sms.db")

# if not database.open():
#     QMessageBox.critical(None, "Error", "Could not open database")
#     sys.exit(1)

# if __name__ == '__main__':

#     print("here")

#     app = QApplication(sys.argv)
#     window = MainWindow()
#     window.show()

#     # Run the application event loop
#     exit_code = app.exec_()

#     sys.exit(exit_code)
