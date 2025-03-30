from PyQt5.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QWidget, QHeaderView, \
    QLabel, QPushButton, QLineEdit, QTableWidget, QMessageBox, QTableWidgetItem, QScrollArea, QDialog, QFormLayout, QComboBox
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlError
from PyQt5.QtCore import Qt
import sys

class AddProductDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Product")
        self.setFixedSize(400, 300)

        # Keep QLineEdit for these fields
        self.product_name = QLineEdit()
        self.price = QLineEdit()
        self.stock_level = QLineEdit()
        self.restock_level = QLineEdit()

        # Replace QLineEdit with QComboBox for these fields
        self.category_combo = QComboBox()
        self.supplier_combo = QComboBox()
        self.discount_combo = QComboBox()

        # Set up dropdown properties
        self.category_combo.setMaxVisibleItems(5)
        self.supplier_combo.setMaxVisibleItems(5)
        self.discount_combo.setMaxVisibleItems(5)
        self.category_combo.setStyleSheet("QComboBox { combobox-popup: 0; }")
        self.supplier_combo.setStyleSheet("QComboBox { combobox-popup: 0; }")
        self.discount_combo.setStyleSheet("QComboBox { combobox-popup: 0; }")

        # Load data into dropdowns
        self.load_categories()
        self.load_suppliers()
        self.load_discounts()

        # Layout
        layout = QFormLayout()
        layout.addRow("Product Name:", self.product_name)
        layout.addRow("Category:", self.category_combo)
        layout.addRow("Price:", self.price)
        layout.addRow("Stock Level:", self.stock_level)
        layout.addRow("Restock Level:", self.restock_level)
        layout.addRow("Supplier ID:", self.supplier_combo)
        layout.addRow("Discount ID:", self.discount_combo)

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

    def load_categories(self):
        """Load category IDs and names into the combo box"""
        self.category_combo.clear()
        self.category_combo.addItem("None", None)  # Optional: Add a "None" option
        query = QSqlQuery("SELECT CategoryID, CategoryName FROM Category")
        while query.next():
            category_id = query.value(0)
            category_name = query.value(1)
            self.category_combo.addItem(category_name, category_id)

    def load_suppliers(self):
        """Load supplier IDs and names into the combo box"""
        self.supplier_combo.clear()
        self.supplier_combo.addItem("None", None)  # Optional: Add a "None" option
        query = QSqlQuery("SELECT SupplierID, SupplierName FROM Suppliers")
        while query.next():
            supplier_id = query.value(0)
            supplier_name = query.value(1)
            self.supplier_combo.addItem(supplier_name, supplier_id)

    def load_discounts(self):
        """Load discount IDs and values into the combo box"""
        self.discount_combo.clear()
        self.discount_combo.addItem("None", None)  # Optional: Add a "None" option
        query = QSqlQuery("SELECT DiscountID, DiscountValue FROM Discount")
        while query.next():
            discount_id = query.value(0)
            discount_value = query.value(1)
            self.discount_combo.addItem(str(discount_value), discount_id)

    def get_category_id(self):
        return self.category_combo.currentData()

    def get_supplier_id(self):
        return self.supplier_combo.currentData()

    def get_discount_id(self):
        return self.discount_combo.currentData()

class DeleteProductDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Delete Product")
        self.setFixedSize(300, 150)

        self.product_combo = QComboBox()
        self.product_combo.setMaxVisibleItems(5)
        self.product_combo.setStyleSheet("QComboBox { combobox-popup: 0; }")
        self.load_products()

        layout = QFormLayout()
        layout.addRow("Select Product:", self.product_combo)

        self.button_box = QHBoxLayout()
        self.ok_btn = QPushButton("Delete")
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

    def get_selected_product_id(self):
        return self.product_combo.currentData()

class ProductPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent

        self.setWindowTitle("Product Management Page")
        self.resize(870, 600)

        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Enter product name...")
        self.search_field.textChanged.connect(self.filter_table)
        
        self.add_btn = QPushButton("Add Product")
        self.del_btn = QPushButton("Delete Product")
        self.back_btn = QPushButton("Back to Main Page")
        self.back_btn.clicked.connect(self.main_window.show_main)
        
        self.add_btn.clicked.connect(self.show_add_product_dialog)
        self.del_btn.clicked.connect(self.show_delete_product_dialog)
        
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["ProductID", "Product Name", "Category", "Price",
                                              "Stock Level", "Restock Level", "Supplier ID", "Discount ID"])

        # Make the table read-only
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        # Make the entire row get selected when any item in it is clicked
        self.table.setSelectionBehavior(QTableWidget.SelectRows)

        # Fit the table within the screen (remove horizontal scrollbar)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # Stretch columns to fit the table width
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Optional: disable horizontal scrollbar


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
        self.row1.addWidget(self.del_btn)

        self.back_btn.setFixedSize(200, 30)
        self.back_btn_layout = QHBoxLayout()
        self.back_btn_layout.addStretch()
        self.back_btn_layout.addWidget(self.back_btn)
        self.back_btn_layout.addStretch()

        self.master_layout.addLayout(self.row1)
        self.master_layout.addWidget(self.scroll_area)
        self.master_layout.addLayout(self.back_btn_layout)

        self.search_field.setStyleSheet("padding: 5px;")
        self.add_btn.setStyleSheet("padding: 5px;")
        self.del_btn.setStyleSheet("padding: 5px;")
        self.back_btn.setStyleSheet("padding: 5px;")

        self.setLayout(self.master_layout)
        self.load_table()

    def load_table(self, filter_text=""):
        self.table.setRowCount(0)
        query = QSqlQuery()
        if filter_text:
            query.prepare("SELECT * FROM Product WHERE ProductName LIKE ?")
            query.addBindValue(f"%{filter_text}%")
        else:
            query.prepare("SELECT * FROM Product")
        
        if not query.exec_():
            print(f"Load table error: {query.lastError().text()}")
            return
            
        while query.next():
            row = self.table.rowCount()
            self.table.insertRow(row)
            for i in range(8):
                self.table.setItem(row, i, QTableWidgetItem(str(query.value(i) or "")))

    def filter_table(self, text):
        self.load_table(text)

    def show_add_product_dialog(self):
        dialog = AddProductDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.add_product(
                dialog.product_name.text(),
                dialog.get_category_id(),
                dialog.price.text(),
                dialog.stock_level.text(),
                dialog.restock_level.text(),
                dialog.get_supplier_id(),
                dialog.get_discount_id()
            )

    def show_delete_product_dialog(self):
        dialog = DeleteProductDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.delete_product(dialog.get_selected_product_id())

    def add_product(self, name, category_id, price, stock, restock, supplier_id, discount_id):
        query = QSqlQuery()
        
        name = name.strip() if name.strip() else None
        try:
            price = float(price.strip()) if price.strip() else None
            stock = int(stock.strip()) if stock.strip() else None
            restock = int(restock.strip()) if restock.strip() else None
        except ValueError as e:
            QMessageBox.critical(self, "Error", f"Invalid input: {e}")
            return

        values = [name, category_id, price, stock, restock, supplier_id, discount_id]
        print("Attempting to insert values:", values)
        
        query.prepare("""
            INSERT INTO Product (ProductName, CategoryID, Price, StockLevel, RestockLevel, SupplierID, DiscountID)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """)
        
        query.addBindValue(name if name is not None else "")
        query.addBindValue(category_id if category_id is not None else None)
        query.addBindValue(price if price is not None else 0.0)
        query.addBindValue(stock if stock is not None else 0)
        query.addBindValue(restock if restock is not None else 0)
        query.addBindValue(supplier_id if supplier_id is not None else None)
        query.addBindValue(discount_id if discount_id is not None else None)
        
        if not query.exec_():
            error = query.lastError().text()
            print(f"Query error: {error}")
            print(f"Bound values: {query.boundValues()}")
            QMessageBox.critical(self, "Error", f"Error adding product: {error}")
        else:
            self.load_table()
            QMessageBox.information(self, "Success", "Product added successfully")

    def delete_product(self, product_id):
        if not product_id:
            QMessageBox.warning(self, "Error", "No product selected")
            return

        confirm = QMessageBox.question(self, "Are you sure?", f"Delete product with ID {product_id}?", 
                                       QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.No:
            return
            
        query = QSqlQuery()
        query.prepare("DELETE FROM Product WHERE ProductID = ?")
        query.addBindValue(product_id)
        
        if not query.exec_():
            QMessageBox.critical(self, "Error", f"Error deleting product: {query.lastError().text()}")
        else:
            self.load_table()
            QMessageBox.information(self, "Success", "Product deleted successfully")

    def delete_discount(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "No row selected", "Please select a row to delete")
            return
        product_id = int(self.table.item(selected_row, 0).text())

        confirm = QMessageBox.question(self, "Are you sure?", "Delete Product?", 
                                       QMessageBox.Yes | QMessageBox.No)

        if confirm == QMessageBox.No:
            return
            
        query = QSqlQuery()
        query.prepare("DELETE FROM Product WHERE ProductID = ?")
        query.addBindValue(product_id)
        if not query.exec_():
            QMessageBox.critical(self, "Error", f"Error deleting product: {query.lastError().text()}")
        else:
            self.load_table()

def check_table_schema():
    query = QSqlQuery()
    if query.exec_("PRAGMA table_info(Product);"):
        print("Product table schema:")
        while query.next():
            print(f"Column: {query.value(1)}, Type: {query.value(2)}, NotNull: {query.value(3)}, Default: {query.value(4)}, PK: {query.value(5)}")
    else:
        print(f"Schema check error: {query.lastError().text()}")

def create_product_table():
    query = QSqlQuery()
    success = query.exec_("""
        CREATE TABLE IF NOT EXISTS Product (
            ProductID INTEGER PRIMARY KEY AUTOINCREMENT,
            ProductName TEXT NOT NULL,
            Category TEXT NOT NULL,
            Price REAL NOT NULL,
            StockLevel INTEGER NOT NULL,
            RestockLevel INTEGER NOT NULL,
            SupplierID INTEGER,
            DiscountID INTEGER
        )
    """)
    if not success or query.lastError().type() != QSqlError.NoError:
        print(f"Table creation error: {query.lastError().text()}")
    else:
        print("Product table created or already exists.")

# database = QSqlDatabase.addDatabase("QSQLITE")
# database.setDatabaseName("sms.db")

# if not database.open():
#     QMessageBox.critical(None, "Error", "Could not open database")
#     sys.exit(1)

# if __name__ == "__main__":
#     app = QApplication([])
#     create_product_table()
#     check_table_schema()
#     window = ProductPage()
#     window.show()
#     app.exec_()