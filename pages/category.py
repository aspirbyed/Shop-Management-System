# Import Modules
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QWidget, QHeaderView,\
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
        self.aisle_number = QLineEdit()
        
        self.add_btn = QPushButton("Add Category")
        self.del_btn = QPushButton("Delete Category")
        self.add_btn.clicked.connect(self.add_category)
        self.del_btn.clicked.connect(self.delete_category)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Category ID", "Category Name", "Aisle Number"])

        # Make the table read-only
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        # Make the entire row get selected when any item in it is clicked
        self.table.setSelectionBehavior(QTableWidget.SelectRows)

        # Fit the table within the screen (remove horizontal scrollbar)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # Stretch columns to fit the table width
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Optional: disable horizontal scrollbar

        self.master_layout = QVBoxLayout()
        self.row1 = QHBoxLayout()
        self.row2 = QHBoxLayout()

        self.row1.addWidget(QLabel("Category Name:"))
        self.row1.addWidget(self.category_name)
        self.row1.addWidget(QLabel("Aisle Number:"))
        self.row1.addWidget(self.aisle_number)
        self.row2.addWidget(self.add_btn)
        self.row2.addWidget(self.del_btn)

        self.master_layout.addLayout(self.row1)
        self.master_layout.addLayout(self.row2)
        self.master_layout.addWidget(self.table)
        self.master_layout.addWidget(self.back_btn)

        self.setLayout(self.master_layout)

        self.load_table()

    def load_table(self):
        self.table.setRowCount(0)
        query = QSqlQuery("SELECT * FROM Category")
        while query.next():
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(query.value(0))))
            self.table.setItem(row, 1, QTableWidgetItem(query.value(1)))
            self.table.setItem(row, 2, QTableWidgetItem(query.value(2)))

    def add_category(self):
        category = self.category_name.text()
        aisle = self.aisle_number.text()
        query = QSqlQuery()
        query.prepare("INSERT INTO Category (CategoryName, AisleNumber) VALUES (?, ?)")
        query.addBindValue(category)
        query.addBindValue(aisle)
        if query.exec_():
            self.load_table()
            self.category_name.clear()
            self.aisle_number.clear()
        else:
            QMessageBox.critical(self, "Error", "Error adding category")

    def delete_category(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "No row selected", "Please select a row to delete")
            return
        category_id = int(self.table.item(selected_row, 0).text())

        confirm = QMessageBox.question(self, "Are you sure?", "Delete Category?", QMessageBox.Yes | QMessageBox.No)

        if confirm == QMessageBox.No:
            return
        
        query = QSqlQuery()
        query.prepare("DELETE FROM Category WHERE CategoryId = ?")
        query.addBindValue(category_id)
        if query.exec_():
            self.load_table()
        else:
            QMessageBox.critical(self, "Error", "Error deleting category!")

# database = QSqlDatabase.addDatabase("QSQLITE")
# database.setDatabaseName("sms.db")

# if not database.open():
#     QMessageBox.critical(None, "Error", "Could not open database")
#     sys.exit(1)

# if __name__ == "__main__":
#     app = QApplication([])
#     window = CategoryPage()
#     window.show()
#     app.exec_()
