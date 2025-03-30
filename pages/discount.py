# Import Modules
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QWidget, QHeaderView,\
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
        
        self.add_btn = QPushButton("Add Discount")
        self.del_btn = QPushButton("Delete Discount")
        self.add_btn.clicked.connect(self.add_discount)
        self.del_btn.clicked.connect(self.delete_discount)

        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["DiscountID", "DiscountValue"])

        # Make the table read-only
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        # Make the entire row get selected when any item in it is clicked
        self.table.setSelectionBehavior(QTableWidget.SelectRows)

        # Fit the table within the screen (remove horizontal scrollbar)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # Stretch columns to fit the table width
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Optional: disable horizontal scrollbar

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
        query = QSqlQuery("SELECT * FROM Discount")
        while query.next():
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(query.value(0))))
            self.table.setItem(row, 1, QTableWidgetItem(str(query.value(1))))

    def add_discount(self):
        discount = self.discount.text()
        query = QSqlQuery()
        query.prepare("INSERT INTO Discount (DiscountValue) VALUES (?)")
        query.addBindValue(discount)
        if query.exec_():
            self.load_table()
            self.discount.clear()
        else:
            QMessageBox.critical(self, "Error", "Error adding discount")

    def delete_discount(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "No row selected", "Please select a row to delete")
            return
        discount_id = int(self.table.item(selected_row, 0).text())

        confirm = QMessageBox.question(self, "Are you sure?", "Delete Expense?", QMessageBox.Yes | QMessageBox.No)

        if confirm == QMessageBox.No:
            return
        
        query = QSqlQuery()
        query.prepare("DELETE FROM discount WHERE DiscountId = ?")
        query.addBindValue(discount_id)
        if query.exec_():
            self.load_table()
        else:
            QMessageBox.critical(self, "Error", "Error deleting discount")

# database = QSqlDatabase.addDatabase("QSQLITE")
# database.setDatabaseName("sms.db")

# if not database.open():
#     QMessageBox.critical(None, "Error", "Could not open database")
#     sys.exit(1)

# if __name__ == "__main__":
#     app = QApplication([])
#     window = DiscountPage()
#     window.show()
#     app.exec_()
