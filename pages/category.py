# Import Modules
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QWidget, QHeaderView, \
    QLabel, QPushButton, QLineEdit, QTableWidget, QMessageBox, QTableWidgetItem
from PyQt5.QtSql import QSqlDatabase, QSqlQuery
from PyQt5.QtCore import Qt
import sys

class CategoryPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent

        self.setWindowTitle("Category Page")
        self.resize(550,500)

        self.back_btn = QPushButton("Back to Main Page")
        self.back_btn.clicked.connect(self.main_window.show_main)

        self.category_name = QLineEdit()
        self.category_name.setStyleSheet("padding: 5px;")
        self.category_name.setPlaceholderText("Enter Category Name...")
        self.aisle_number = QLineEdit()
        self.aisle_number.setStyleSheet("padding: 5px;")
        self.aisle_number.setPlaceholderText("Enter Aisle Number...")
        
        self.add_btn = QPushButton("Add Category")
        self.add_btn.setFixedSize(150,30)
        self.del_btn = QPushButton("Delete Category")
        self.del_btn.setFixedSize(150,30)
        self.add_btn.clicked.connect(self.add_category)
        self.del_btn.clicked.connect(self.delete_category)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Category Name", "Aisle Number", "Category ID"])  # Updated headers

        # Make the table read-only
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        # Make the entire row get selected when any item in it is clicked
        self.table.setSelectionBehavior(QTableWidget.SelectRows)

        # Fit the table within the screen (remove horizontal scrollbar)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.master_layout = QVBoxLayout()
        self.row1 = QHBoxLayout()
        self.row2 = QHBoxLayout()

        self.row1.addWidget(QLabel("Category Name:"))
        self.row1.addWidget(self.category_name)
        self.row1.addWidget(QLabel("Aisle Number:"))
        self.row1.addWidget(self.aisle_number)
        self.row2.addWidget(self.add_btn)
        self.row2.addWidget(self.del_btn)
        self.row2.addStretch()

        self.back_btn.setFixedSize(200, 30)
        self.back_btn_layout = QHBoxLayout()
        self.back_btn_layout.addStretch()
        self.back_btn_layout.addWidget(self.back_btn)
        self.back_btn_layout.addStretch()

        self.master_layout.addLayout(self.row1)
        self.master_layout.addLayout(self.row2)
        self.master_layout.addWidget(self.table)
        self.master_layout.addLayout(self.back_btn_layout)

        self.setLayout(self.master_layout)

        self.load_table()

    def load_table(self):
        self.table.setRowCount(0)
        query = QSqlQuery("SELECT CategoryName, AisleNumber, CategoryID FROM Category")  # Updated query order
        while query.next():
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(query.value(0))))  # CategoryName
            self.table.setItem(row, 1, QTableWidgetItem(str(query.value(1))))  # AisleNumber
            self.table.setItem(row, 2, QTableWidgetItem(str(query.value(2))))  # CategoryID

    def add_category(self):
        category = self.category_name.text().strip()
        aisle = self.aisle_number.text().strip()

        if not category:
            QMessageBox.warning(self, "Error", "Category name cannot be empty!")
            return

        # Check if category name already exists
        check_query = QSqlQuery()
        check_query.prepare("SELECT COUNT(*) FROM Category WHERE CategoryName = ?")
        check_query.addBindValue(category)
        if check_query.exec_() and check_query.next():
            if check_query.value(0) > 0:
                QMessageBox.warning(self, "Error", "A category with this name already exists!")
                return

        query = QSqlQuery()
        query.prepare("INSERT INTO Category (CategoryName, AisleNumber) VALUES (?, ?)")
        query.addBindValue(category)
        query.addBindValue(aisle)
        if query.exec_():
            self.load_table()
            self.category_name.clear()
            self.aisle_number.clear()
            QMessageBox.information(self, "Success", "Category added successfully")
        else:
            QMessageBox.critical(self, "Error", f"Error adding category: {query.lastError().text()}")

    def delete_category(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "No row selected", "Please select a row to delete")
            return
        category_name = self.table.item(selected_row, 0).text()  # Changed to use CategoryName

        confirm = QMessageBox.question(self, "Are you sure?", f"Delete category '{category_name}'?", 
                                     QMessageBox.Yes | QMessageBox.No)

        if confirm == QMessageBox.No:
            return
        
        query = QSqlQuery()
        query.prepare("DELETE FROM Category WHERE CategoryName = ?")  # Changed to use CategoryName
        query.addBindValue(category_name)
        if query.exec_():
            self.load_table()
            QMessageBox.information(self, "Success", "Category deleted successfully")
        else:
            QMessageBox.critical(self, "Error", f"Error deleting category: {query.lastError().text()}")

# Database setup
database = QSqlDatabase.addDatabase("QSQLITE")
database.setDatabaseName("sms.db")

# if not database.open():
#     QMessageBox.critical(None, "Error", "Could not open database")
#     sys.exit(1)

# # Create Category table if it doesn't exist
# def create_category_table():
#     query = QSqlQuery()
#     success = query.exec_("""
#         CREATE TABLE IF NOT EXISTS Category (
#             CategoryName TEXT PRIMARY KEY NOT NULL,
#             AisleNumber TEXT NOT NULL,
#             CategoryID INTEGER
#         )
#     """)
#     if not success:
#         print(f"Table creation error: {query.lastError().text()}")
#     else:
#         print("Category table created or already exists.")

# if __name__ == "__main__":
#     app = QApplication([])
#     create_category_table()
#     window = CategoryPage()
#     window.show()
#     app.exec_()
