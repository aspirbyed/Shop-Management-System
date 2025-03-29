from PyQt5.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QWidget, \
    QLabel, QPushButton, QLineEdit, QTableWidget, QMessageBox, QTableWidgetItem, QScrollArea, QDialog, QFormLayout, QComboBox
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlError
from PyQt5.QtCore import Qt,QDateTime
from datetime import datetime
import sys

class AddStockDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Stock")
        self.setFixedSize(300, 200)

        self.product_combo = QComboBox()
        self.quantity = QLineEdit()
        self.supplier_combo = QComboBox()

        self.product_combo.setMaxVisibleItems(5)
        self.supplier_combo.setMaxVisibleItems(5)
        self.product_combo.setStyleSheet("QComboBox { combobox-popup: 0; }")
        self.supplier_combo.setStyleSheet("QComboBox { combobox-popup: 0; }")

        self.load_products()
        self.load_suppliers()

        layout = QFormLayout()
        layout.addRow("Product Name:", self.product_combo)
        layout.addRow("Quantity:", self.quantity)
        layout.addRow("Supplier:", self.supplier_combo)

        self.button_box = QHBoxLayout()
        self.ok_btn = QPushButton("OK")
        self.cancel_btn = QPushButton("Cancel")
        self.button_box.addWidget(self.ok_btn)
        self.button_box.addWidget(self.cancel_btn)

        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addLayout(self.button_box)
        self.setLayout(main_layout)

    def load_products(self):
        self.product_combo.clear()
        query = QSqlQuery("SELECT ProductID, ProductName FROM Product")
        while query.next():
            product_id = query.value(0)
            product_name = query.value(1)
            self.product_combo.addItem(product_name, product_id)

    def load_suppliers(self):
        self.supplier_combo.clear()
        self.supplier_combo.addItem("None", None)
        query = QSqlQuery("SELECT SupplierID, SupplierName FROM Suppliers")
        while query.next():
            supplier_id = query.value(0)
            supplier_name = query.value(1)
            self.supplier_combo.addItem(supplier_name, supplier_id)

    def get_product_id(self):
        return self.product_combo.currentData()

    def get_supplier_id(self):
        return self.supplier_combo.currentData()

class StockPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent

        self.setWindowTitle("Stock Management Page")
        self.resize(870, 600)

        self.back_btn = QPushButton("Back to Main Page")
        self.back_btn.clicked.connect(self.main_window.show_main)

        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Enter product name...")
        self.search_field.textChanged.connect(self.filter_table)
        
        self.add_btn = QPushButton("Add Stock")
        # self.back_btn = QPushButton("Back")
        
        self.add_btn.clicked.connect(self.show_add_stock_dialog)
        
        # self.back_btn.setFixedSize(100, 30)
        
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ProductID", "ProductName", "StockLevel", "RestockLevel"])

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.table)
        self.scroll_area.setWidgetResizable(True)

        self.master_layout = QVBoxLayout()
        self.row1 = QHBoxLayout()

        self.master_layout.setSpacing(10)
        self.master_layout.setContentsMargins(15, 15, 15, 15)
        self.row1.setSpacing(10)

        self.row1.addWidget(QLabel("Search:"))
        self.row1.addWidget(self.search_field)
        self.row1.addWidget(self.add_btn)

        back_btn_layout = QHBoxLayout()
        back_btn_layout.addStretch()
        back_btn_layout.addWidget(self.back_btn)
        back_btn_layout.addStretch()

        self.master_layout.addLayout(self.row1)
        self.master_layout.addWidget(self.scroll_area)
        self.master_layout.addLayout(back_btn_layout)

        self.search_field.setStyleSheet("padding: 5px;")
        self.add_btn.setStyleSheet("padding: 5px;")
        self.back_btn.setStyleSheet("padding: 5px;")

        self.setLayout(self.master_layout)
        self.load_table()

    def load_table(self, filter_text=""):
        self.table.setRowCount(0)
        query = QSqlQuery()
        if filter_text:
            query.prepare("""
                SELECT ProductID, ProductName, StockLevel, RestockLevel
                FROM Product
                WHERE ProductName LIKE ?
            """)
            query.addBindValue(f"%{filter_text}%")
        else:
            query.prepare("SELECT ProductID, ProductName, StockLevel, RestockLevel FROM Product")
        
        if not query.exec_():
            print(f"Load table error: {query.lastError().text()}")
            return
            
        while query.next():
            row = self.table.rowCount()
            self.table.insertRow(row)
            for i in range(4):
                self.table.setItem(row, i, QTableWidgetItem(str(query.value(i) or "")))

    def filter_table(self, text):
        self.load_table(text)

    def show_add_stock_dialog(self):
        dialog = AddStockDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.add_stock(
                dialog.get_product_id(),
                dialog.quantity.text(),
                dialog.get_supplier_id()
            )

    def add_stock(self, product_id, quantity, supplier_id):
        query = QSqlQuery()
        
        try:
            quantity = int(quantity.strip()) if quantity.strip() else None
            if not product_id or quantity is None:
                raise ValueError("Product and Quantity are required")
        except ValueError as e:
            QMessageBox.critical(self, "Error", f"Invalid input: {e}")
            return

        # Get current stock level
        query.prepare("SELECT StockLevel FROM Product WHERE ProductID = ?")
        query.addBindValue(product_id)
        if not query.exec_() or not query.next():
            QMessageBox.critical(self, "Error", f"Error fetching stock level: {query.lastError().text()}")
            return
        current_stock = int(query.value(0) or 0)

        # Update StockLevel in Product table
        new_stock = current_stock + quantity
        query.prepare("UPDATE Product SET StockLevel = ? WHERE ProductID = ?")
        query.addBindValue(new_stock)
        query.addBindValue(product_id)
        if not query.exec_():
            QMessageBox.critical(self, "Error", f"Error updating stock: {query.lastError().text()}")
            return

        # Add entry to InventoryTransactions
        transaction_time= QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
        query.prepare("""
            INSERT INTO InventoryTransactions (ProductID, TransactionType, Quantity, TransactionDate, SupplierID)
            VALUES (?, ?, ?, ?, ?)
        """)
        query.addBindValue(product_id)
        query.addBindValue("In")
        query.addBindValue(quantity)
        query.addBindValue(transaction_time)
        query.addBindValue(supplier_id if supplier_id else None)
        
        if not query.exec_():
            error = query.lastError().text()
            print(f"Query error: {error}")
            print(f"Bound values: {query.boundValues()}")
            QMessageBox.critical(self, "Error", f"Error adding transaction: {error}")
        else:
            self.load_table()
            QMessageBox.information(self, "Success", "Stock added successfully")

def check_table_schema():
    query = QSqlQuery()
    for table in ["Product", "InventoryTransactions"]:
        if query.exec_(f"PRAGMA table_info({table});"):
            print(f"{table} table schema:")
            while query.next():
                print(f"Column: {query.value(1)}, Type: {query.value(2)}, NotNull: {query.value(3)}, Default: {query.value(4)}, PK: {query.value(5)}")
        else:
            print(f"Schema check error for {table}: {query.lastError().text()}")

# database = QSqlDatabase.addDatabase("QSQLITE")
# database.setDatabaseName("sms.db")

# if not database.open():
#     QMessageBox.critical(None, "Error", "Could not open database")
#     sys.exit(1)

# if __name__ == "__main__":
#     app = QApplication([])
#     check_table_schema()
#     window = StockPage()
#     window.show()
#     app.exec_()
