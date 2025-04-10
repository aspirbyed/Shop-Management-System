# Johan
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QHeaderView, QWidget, \
    QLabel, QPushButton, QLineEdit, QTableWidget, QMessageBox, QTableWidgetItem
from PyQt5.QtCore import Qt
from PyQt5.QtSql import QSqlDatabase, QSqlQuery
import sys

class SuppliersPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent

        self.setWindowTitle("Suppliers Page")
        self.resize(600, 500)

        self.back_btn = QPushButton("Back to Main Page")
        self.back_btn.clicked.connect(self.main_window.show_main)

        # Input fields for supplier details
        self.supplier_name = QLineEdit()
        self.supplier_name.setStyleSheet("padding: 5px;")
        self.supplier_name.setPlaceholderText("Enter Name...")
        self.supplier_contact = QLineEdit()
        self.supplier_contact.setStyleSheet("padding: 5px;")
        self.supplier_contact.setPlaceholderText("Enter Contact No...")
        self.supplier_address = QLineEdit()
        self.supplier_address.setStyleSheet("padding: 5px;")
        self.supplier_address.setPlaceholderText("Enter Address...")

        # Buttons
        self.add_btn = QPushButton("Add Supplier")
        self.add_btn.setFixedSize(150,30)
        self.del_btn = QPushButton("Delete Supplier")
        self.del_btn.setFixedSize(150,30)
        self.add_btn.clicked.connect(self.add_supplier)
        self.del_btn.clicked.connect(self.delete_supplier)

        # Table to display suppliers
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["SupplierID", "Name", "Contact", "Address"])
        self.table.clicked.connect(self.load_selected_row)  # Load row data into fields when clicked

        # Make the table read-only
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        # Make the entire row get selected when any item in it is clicked
        self.table.setSelectionBehavior(QTableWidget.SelectRows)

        # Fit the table within the screen (remove horizontal scrollbar)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Layouts
        self.master_layout = QVBoxLayout()
        self.row1 = QHBoxLayout()
        self.row2 = QHBoxLayout()
        self.row3 = QHBoxLayout()

        self.row1.addWidget(QLabel("Supplier Name:"))
        self.row1.addWidget(self.supplier_name, 1)
        self.row1.addWidget(QLabel("Contact:"))
        self.row1.addWidget(self.supplier_contact, 1)
        self.row1.addWidget(QLabel("Address:"))
        self.row1.addWidget(self.supplier_address, 2)
        self.row1.addStretch()

        # Row 3: Buttons
        self.row3.addWidget(self.add_btn)
        self.row3.addWidget(self.del_btn)
        self.row3.addStretch()

        self.back_btn.setFixedSize(200, 30)
        self.back_btn_layout = QHBoxLayout()
        self.back_btn_layout.addStretch()
        self.back_btn_layout.addWidget(self.back_btn)
        self.back_btn_layout.addStretch()

        # Add layouts to master layout
        self.master_layout.addLayout(self.row1)
        self.master_layout.addLayout(self.row2)
        self.master_layout.addLayout(self.row3)
        self.master_layout.addWidget(self.table)
        self.master_layout.addLayout(self.back_btn_layout)

        self.setLayout(self.master_layout)

        # Load initial table data
        self.load_table()

    def load_table(self):
        """Load supplier data into the table."""
        self.table.setRowCount(0)
        query = QSqlQuery("SELECT SupplierID, SupplierName, ContactNumber, Address FROM Suppliers")
        while query.next():
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(query.value(0))))  # SupplierID
            self.table.setItem(row, 1, QTableWidgetItem(query.value(1)))       # SupplierName
            self.table.setItem(row, 2, QTableWidgetItem(query.value(2)))       # ContactNumber
            self.table.setItem(row, 3, QTableWidgetItem(query.value(3)))       # Address 

    def load_selected_row(self):
        """Populate input fields with data from the selected row."""
        selected_row = self.table.currentRow()
        if selected_row != -1:
            self.supplier_name.setText(self.table.item(selected_row, 1).text())
            self.supplier_contact.setText(self.table.item(selected_row, 2).text())
            self.supplier_address.setText(self.table.item(selected_row, 3).text())

    def add_supplier(self):
        """Add a new supplier to the database."""
        name = self.supplier_name.text().strip()
        contact = self.supplier_contact.text().strip()
        address = self.supplier_address.text().strip()

        if not name or not contact or not address:
            QMessageBox.warning(self, "Input Error", "Please enter all fields: name, contact, and address.")
            return

        # Check if supplier name already exists
        check_query = QSqlQuery()
        check_query.prepare("SELECT COUNT(*) FROM Suppliers WHERE SupplierName = ?")
        check_query.addBindValue(name)
        if check_query.exec_() and check_query.next():
            if check_query.value(0) > 0:
                QMessageBox.warning(self, "Error", "A supplier with this name already exists!")
                return

        query = QSqlQuery()
        query.prepare("INSERT INTO Suppliers (SupplierName, ContactNumber, Address) VALUES (?, ?, ?)")
        query.addBindValue(name)
        query.addBindValue(contact)
        query.addBindValue(address)

        if query.exec_():
            self.load_table()
            self.clear_fields()
            QMessageBox.information(self, "Success", "Supplier added successfully")
        else:
            QMessageBox.critical(self, "Error", f"Error adding supplier: {query.lastError().text()}")

    def delete_supplier(self):
        """Delete the selected supplier from the database."""
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "No Selection", "Please select a supplier to delete.")
            return

        supplier_name = self.table.item(selected_row, 1).text()  # Use SupplierName for confirmation
        confirm = QMessageBox.question(self, "Confirm Delete", f"Are you sure you want to delete supplier '{supplier_name}'?",
                                       QMessageBox.Yes | QMessageBox.No)

        if confirm == QMessageBox.No:
            return

        query = QSqlQuery()
        query.prepare("DELETE FROM Suppliers WHERE SupplierName = ?")  # Changed to use SupplierName
        query.addBindValue(supplier_name)

        if query.exec_():
            self.load_table()
            self.clear_fields()
            QMessageBox.information(self, "Success", "Supplier deleted successfully")
        else:
            QMessageBox.critical(self, "Error", f"Error deleting supplier: {query.lastError().text()}")

    def clear_fields(self):
        """Clear the input fields."""
        self.supplier_name.clear()
        self.supplier_contact.clear()
        self.supplier_address.clear()

# Database Setup
database = QSqlDatabase.addDatabase("QSQLITE")
database.setDatabaseName("sms.db")

# if not database.open():
#     QMessageBox.critical(None, "Error", "Could not open database")
#     sys.exit(1)

# # Create Suppliers table if it doesn't exist
# def create_suppliers_table():
#     query = QSqlQuery()
#     success = query.exec_("""
#         CREATE TABLE IF NOT EXISTS Suppliers (
#             SupplierName TEXT PRIMARY KEY NOT NULL,
#             ContactNumber TEXT,
#             Address TEXT,
#             SupplierID INTEGER
#         )
#     """)
#     if not success:
#         print(f"Table creation error: {query.lastError().text()}")
#     else:
#         print("Suppliers table created or already exists.")

# if __name__ == "__main__":
#     app = QApplication([])
#     create_suppliers_table()
#     window = SuppliersPage()
#     window.show()
#     app.exec_()
