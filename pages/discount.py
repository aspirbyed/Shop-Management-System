# Import Modules
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QWidget, QHeaderView, \
    QLabel, QPushButton, QLineEdit, QTableWidget, QMessageBox, QTableWidgetItem
from PyQt5.QtSql import QSqlDatabase, QSqlQuery
from PyQt5.QtCore import Qt
import sys

class DiscountPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent

        self.setWindowTitle("Discount Page")
        self.resize(550,500)

        self.back_btn = QPushButton("Back to Main Page")
        self.back_btn.clicked.connect(self.main_window.show_main)

        self.discount = QLineEdit()
        self.discount.setStyleSheet("padding: 5px;")
        self.discount.setPlaceholderText("Enter Discount Value...")
        
        self.add_btn = QPushButton("Add Discount")
        self.add_btn.setFixedSize(150, 30)  # Added fixed size for consistency
        self.del_btn = QPushButton("Delete Discount")
        self.del_btn.setFixedSize(150, 30)  # Added fixed size for consistency
        self.add_btn.clicked.connect(self.add_discount)
        self.del_btn.clicked.connect(self.delete_discount)

        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Discount ID", "Discount Value"])  # Updated headers

        # Make the table read-only
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        # Make the entire row get selected when any item in it is clicked
        self.table.setSelectionBehavior(QTableWidget.SelectRows)

        # Fit the table within the screen (remove horizontal scrollbar)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.master_layout = QVBoxLayout()
        self.row1 = QHBoxLayout()

        self.row1.addWidget(QLabel("Discount:"))
        self.row1.addWidget(self.discount)
        self.row1.addWidget(self.add_btn)
        self.row1.addWidget(self.del_btn)

        self.back_btn.setFixedSize(200, 30)
        self.back_btn_layout = QHBoxLayout()
        self.back_btn_layout.addStretch()
        self.back_btn_layout.addWidget(self.back_btn)
        self.back_btn_layout.addStretch()

        self.master_layout.addLayout(self.row1)
        self.master_layout.addWidget(self.table)
        self.master_layout.addLayout(self.back_btn_layout)

        self.setLayout(self.master_layout)

        self.load_table()

    def load_table(self):
        self.table.setRowCount(0)
        query = QSqlQuery("SELECT DiscountID, DiscountValue FROM Discount")  # Updated query order
        while query.next():
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(query.value(0))))  # DiscountValue
            self.table.setItem(row, 1, QTableWidgetItem(str(query.value(1))))  # DiscountID

    def add_discount(self):
        discount = self.discount.text().strip()
        
        if not discount:
            QMessageBox.warning(self, "Error", "Discount value cannot be empty!")
            return
            
        try:
            discount_value = float(discount)
        except ValueError:
            QMessageBox.critical(self, "Error", "Invalid Discount Value - must be a number!")
            return

        # Check if discount value already exists
        check_query = QSqlQuery()
        check_query.prepare("SELECT COUNT(*) FROM Discount WHERE DiscountValue = ?")
        check_query.addBindValue(discount_value)
        if check_query.exec_() and check_query.next():
            if check_query.value(0) > 0:
                QMessageBox.warning(self, "Error", "A discount with this value already exists!")
                return

        query = QSqlQuery()
        query.prepare("INSERT INTO Discount (DiscountValue) VALUES (?)")
        query.addBindValue(discount_value)
        if query.exec_():
            self.load_table()
            self.discount.clear()
            QMessageBox.information(self, "Success", "Discount added successfully")
        else:
            QMessageBox.critical(self, "Error", f"Error adding discount: {query.lastError().text()}")

    def delete_discount(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "No row selected", "Please select a row to delete")
            return
        discount_value = float(self.table.item(selected_row, 0).text())  # Changed to use DiscountValue

        confirm = QMessageBox.question(self, "Are you sure?", f"Delete discount value {discount_value}?", 
                                     QMessageBox.Yes | QMessageBox.No)

        if confirm == QMessageBox.No:
            return
        
        query = QSqlQuery()
        query.prepare("DELETE FROM Discount WHERE DiscountValue = ?")  # Changed to use DiscountValue
        query.addBindValue(discount_value)
        if query.exec_():
            self.load_table()
            QMessageBox.information(self, "Success", "Discount deleted successfully")
        else:
            QMessageBox.critical(self, "Error", f"Error deleting discount: {query.lastError().text()}")

# Database setup
database = QSqlDatabase.addDatabase("QSQLITE")
database.setDatabaseName("sms.db")

# if not database.open():
#     QMessageBox.critical(None, "Error", "Could not open database")
#     sys.exit(1)

# # Create Discount table if it doesn't exist
# def create_discount_table():
#     query = QSqlQuery()
#     success = query.exec_("""
#         CREATE TABLE IF NOT EXISTS Discount (
#             DiscountValue REAL PRIMARY KEY NOT NULL,
#             DiscountID INTEGER
#         )
#     """)
#     if not success:
#         print(f"Table creation error: {query.lastError().text()}")
#     else:
#         print("Discount table created or already exists.")

# if __name__ == "__main__":
#     app = QApplication([])
#     create_discount_table()
#     window = DiscountPage()
#     window.show()
#     app.exec_()
