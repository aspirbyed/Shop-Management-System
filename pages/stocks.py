from PyQt5.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QWidget, QHeaderView, \
    QLabel, QPushButton, QLineEdit, QTableWidget, QMessageBox, QTableWidgetItem, QScrollArea, QDialog, QFormLayout, QComboBox
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlError
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtGui import QColor, QBrush
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
        # Initial load of suppliers based on first product
        self.update_suppliers()

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

    def update_suppliers(self):
        # Get the currently selected product ID
        product_id = self.get_product_id()
        if product_id is None:
            return
            
        self.supplier_combo.clear()
        self.supplier_combo.addItem("None", None)
        
        # Query to get suppliers who have supplied this product
        query = QSqlQuery()
        query.prepare("""
            SELECT s.SupplierID, s.SupplierName
            FROM Suppliers s
            WHERE s.SupplierID IN (
                      SELECT p.SupplierID
                      FROM Product p
                      WHERE p.ProductID = ?
                      )
        """)
        query.addBindValue(product_id)
        
        if not query.exec_():
            print(f"Supplier query error: {query.lastError().text()}")
            return
            
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
        self.add_btn.setFixedSize(100,30)
        # self.back_btn = QPushButton("Back")
        
        self.add_btn.clicked.connect(self.show_add_stock_dialog)
        
        # self.back_btn.setFixedSize(100, 30)
        
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ProductID", "ProductName", "StockLevel", "RestockLevel"])

        # Make the table read-only
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        # Make the entire row get selected when any item in it is clicked
        self.table.setSelectionBehavior(QTableWidget.SelectRows)

        # Fit the table within the screen (remove horizontal scrollbar)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # Stretch columns to fit the table width
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Optional: disable horizontal scrollbar

        # Add a label to explain the highlighting
        self.highlight_label = QLabel("Highlighted rows indicate stock level below restock level")
        self.highlight_label.setStyleSheet("color: #0066CC; font-style: italic;")

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

        self.back_btn.setFixedSize(200, 30)
        self.back_btn_layout = QHBoxLayout()
        self.back_btn_layout.addStretch()
        self.back_btn_layout.addWidget(self.back_btn)
        self.back_btn_layout.addStretch()

        self.master_layout.addLayout(self.row1)
        self.master_layout.addWidget(self.highlight_label)
        self.master_layout.addWidget(self.scroll_area)
        self.master_layout.addLayout(self.back_btn_layout)

        self.search_field.setStyleSheet("padding: 5px;")
        # self.add_btn.setStyleSheet("padding: 5px;")

        self.setLayout(self.master_layout)
        self.load_table()

    def load_table(self, filter_text=None):
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
            
            product_id = query.value(0)
            product_name = query.value(1)
            stock_level = int(query.value(2) or 0)
            restock_level = int(query.value(3) or 0)
            
            # Create table items with black text
            item0 = QTableWidgetItem(str(product_id))
            item1 = QTableWidgetItem(product_name)
            item2 = QTableWidgetItem(str(stock_level))
            item3 = QTableWidgetItem(str(restock_level))
            
            # Set items to the table
            self.table.setItem(row, 0, item0)
            self.table.setItem(row, 1, item1)
            self.table.setItem(row, 2, item2)
            self.table.setItem(row, 3, item3)
            
            # Highlight the row if stock level is below restock level
            if stock_level < restock_level:
                # Use a light blue background for highlighting
                highlight_color = QColor(200, 220, 255)  # Light blue
                
                for col in range(4):
                    # Set background color to blue
                    self.table.item(row, col).setBackground(highlight_color)
                    # Ensure text color remains black
                    self.table.item(row, col).setForeground(QBrush(Qt.black))

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
