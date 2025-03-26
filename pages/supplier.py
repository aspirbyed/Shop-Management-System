# Johan
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QWidget, \
    QLabel, QPushButton, QLineEdit, QTableWidget, QMessageBox, QTableWidgetItem
from PyQt5.QtSql import QSqlDatabase, QSqlQuery
import sys

class SuppliersPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Suppliers Page")
        self.resize(600, 500)

        # Input fields for supplier details
        self.supplier_name = QLineEdit()
        self.supplier_contact = QLineEdit()

        # Buttons
        self.add_btn = QPushButton("Add Supplier")
        self.update_btn = QPushButton("Update Supplier")
        self.del_btn = QPushButton("Delete Supplier")
        self.add_btn.clicked.connect(self.add_supplier)
        self.update_btn.clicked.connect(self.update_supplier)
        self.del_btn.clicked.connect(self.delete_supplier)

        # Table to display suppliers
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["SupplierID", "Name", "Contact"])
        self.table.clicked.connect(self.load_selected_row)  # Load row data into fields when clicked

        # Layouts
        self.master_layout = QVBoxLayout()
        self.row1 = QHBoxLayout()
        self.row2 = QHBoxLayout()
        self.row3 = QHBoxLayout()

        # Row 1: Supplier Name
        self.row1.addWidget(QLabel("Supplier Name:"))
        self.row1.addWidget(self.supplier_name)

        # Row 2: Contact
        self.row2.addWidget(QLabel("Contact:"))
        self.row2.addWidget(self.supplier_contact)

        # Row 3: Buttons
        self.row3.addWidget(self.add_btn)
        self.row3.addWidget(self.update_btn)
        self.row3.addWidget(self.del_btn)

        # Add layouts to master layout
        self.master_layout.addLayout(self.row1)
        self.master_layout.addLayout(self.row2)
        self.master_layout.addLayout(self.row3)
        self.master_layout.addWidget(self.table)

        self.setLayout(self.master_layout)

        # Load initial table data
        self.load_table()

    def load_table(self):
        """Load supplier data into the table."""
        self.table.setRowCount(0)
        query = QSqlQuery("SELECT SupplierID, SupplierName, ContactNumber FROM Suppliers")
        while query.next():
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(query.value(0))))  # supplierID
            self.table.setItem(row, 1, QTableWidgetItem(query.value(1)))       # supplierName
            self.table.setItem(row, 2, QTableWidgetItem(query.value(2)))       # supplierContact

    def load_selected_row(self):
        """Populate input fields with data from the selected row."""
        selected_row = self.table.currentRow()
        if selected_row != -1:
            self.supplier_name.setText(self.table.item(selected_row, 1).text())
            self.supplier_contact.setText(self.table.item(selected_row, 2).text())

    def add_supplier(self):
        """Add a new supplier to the database."""
        name = self.supplier_name.text().strip()
        contact = self.supplier_contact.text().strip()

        if not name or not contact:
            QMessageBox.warning(self, "Input Error", "Please enter both name and contact.")
            return

        query = QSqlQuery()
        query.prepare("INSERT INTO Suppliers (SupplierName, ContactNumber) VALUES (?, ?)")
        query.addBindValue(name)
        query.addBindValue(contact)

        if query.exec_():
            self.load_table()
            self.clear_fields()
        else:
            QMessageBox.critical(self, "Error", "Error adding supplier: " + query.lastError().text())

    def update_supplier(self):
        """Update the selected supplier's details."""
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "No Selection", "Please select a supplier to update.")
            return

        supplier_id = int(self.table.item(selected_row, 0).text())
        name = self.supplier_name.text().strip()
        contact = self.supplier_contact.text().strip()

        if not name or not contact:
            QMessageBox.warning(self, "Input Error", "Please enter both name and contact.")
            return

        query = QSqlQuery()
        query.prepare("UPDATE Suppliers SET SupplierName = ?, ContactNumber = ? WHERE SupplierID = ?")
        query.addBindValue(name)
        query.addBindValue(contact)
        query.addBindValue(supplier_id)

        if query.exec_():
            self.load_table()
            self.clear_fields()
        else:
            QMessageBox.critical(self, "Error", "Error updating supplier: " + query.lastError().text())

    def delete_supplier(self):
        """Delete the selected supplier from the database."""
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "No Selection", "Please select a supplier to delete.")
            return

        supplier_id = int(self.table.item(selected_row, 0).text())
        confirm = QMessageBox.question(self, "Confirm Delete", "Are you sure you want to delete this supplier?",
                                       QMessageBox.Yes | QMessageBox.No)

        if confirm == QMessageBox.No:
            return

        query = QSqlQuery()
        query.prepare("DELETE FROM Suppliers WHERE SupplierID = ?")
        query.addBindValue(supplier_id)

        if query.exec_():
            self.load_table()
            self.clear_fields()
        else:
            QMessageBox.critical(self, "Error", "Error deleting supplier: " + query.lastError().text())

    def clear_fields(self):
        """Clear the input fields."""
        self.supplier_name.clear()
        self.supplier_contact.clear()

# Database Setup
database = QSqlDatabase.addDatabase("QSQLITE")
database.setDatabaseName("sms.db")

if not database.open():
    QMessageBox.critical(None, "Error", "Could not open database")
    sys.exit(1)

# Create Suppliers table if it doesn't exist
# query = QSqlQuery()
# query.exec_("""
#     CREATE TABLE IF NOT EXISTS Suppliers (
#         supplierID INTEGER PRIMARY KEY AUTOINCREMENT,
#         supplierName TEXT NOT NULL,
#         supplierContact TEXT NOT NULL
#     )
# """)

if __name__ == "__main__":
    app = QApplication([])
    window = SuppliersPage()
    window.show()
    app.exec_()