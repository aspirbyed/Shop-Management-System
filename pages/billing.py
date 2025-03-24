# Import Modules
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QWidget, QHeaderView,\
    QLabel, QPushButton, QTableWidget, QMessageBox, QTableWidgetItem, QComboBox, QDialog,\
    QLineEdit, QDialogButtonBox, QSpinBox
from PyQt5.QtSql import QSqlDatabase, QSqlQuery
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtGui import QIntValidator
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import os
import sys

class PaymentBox(QDialog):
    def __init__(self, total_amount, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Payment")
        self.resize(200,300)
        self.total_amount = total_amount

        self.payment_method = QComboBox()
        self.amount_paid = QLineEdit()
        self.amount_paid.setValidator(QIntValidator(0, 99999999, self))
        self.amount_paid.textChanged.connect(self.calculate_balance)
        self.balance = QLabel("0")

        self.payment_method.addItems(["Cash", "Credit Card", "Debit Card", "UPI"])

        master_layout = QVBoxLayout()

        master_layout.addWidget(QLabel("Payment Method:"))
        master_layout.addWidget(self.payment_method)
        master_layout.addWidget(QLabel("Amount Paid:"))
        master_layout.addWidget(self.amount_paid)
        master_layout.addWidget(QLabel("Balance:"))
        master_layout.addWidget(self.balance)

        # Buttons (OK and Cancel)
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        master_layout.addWidget(self.button_box)

        self.setLayout(master_layout)

    def calculate_balance(self):
        amount = int(self.amount_paid.text())
        balance = max(0, amount - int(self.total_amount))
        self.balance.setText(str(balance))

    def get_payment_details(self):
        method = self.payment_method.currentText()
        try:
            amount = int(self.amount_paid.text())
        except ValueError:
            amount = 0
        return method, amount

class BillingPage(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Billing Page")
        self.resize(550,500)

        # self.table_data = []
        self.subtotal_amount = 0

        self.product_list = QComboBox()
        self.quantity = QSpinBox()
        self.subtotal = QLabel(str(self.subtotal_amount))

        self.add_btn = QPushButton("+")
        self.del_btn = QPushButton("-")
        self.add_btn.setFixedSize(40,30)
        self.del_btn.setFixedSize(40,30)
        self.add_btn.clicked.connect(self.add_product)
        self.del_btn.clicked.connect(self.rem_product)

        self.bill_btn = QPushButton("Checkout")
        self.cancel_btn = QPushButton("Cancel")
        self.bill_btn.setFixedSize(100,30)
        self.cancel_btn.setFixedSize(100,30)
        self.bill_btn.clicked.connect(self.checkout)
        self.cancel_btn.clicked.connect(self.cancel)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Product Name", "Quantity", "Unit Price", "Total Price", "Discount"])

        # Make the table read-only
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        # Make the entire row get selected when any item in it is clicked
        self.table.setSelectionBehavior(QTableWidget.SelectRows)

        # Fit the table within the screen (remove horizontal scrollbar)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # Stretch columns to fit the table width
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Optional: disable horizontal scrollbar

        self.quantity.setMinimum(1)
        self.quantity.setMaximum(100)
        self.quantity.setValue(1)
        self.quantity.setFixedWidth(60)

        self.product_list.addItem("None")
        self.product_list.addItems([x for x in self.set_product_list()])
        self.product_list.setMaxVisibleItems(10)
        self.product_list.setStyleSheet("QComboBox { combobox-popup: 0; }");

        self.master_layout = QVBoxLayout()
        self.row1 = QHBoxLayout()
        self.row2 = QHBoxLayout()
        self.row3 = QHBoxLayout()

        self.row1.addWidget(QLabel("Product Name:"))
        self.row1.addWidget(self.product_list)
        self.row1.addStretch()
        self.row1.addWidget(QLabel("Quantity:"))
        self.row1.addWidget(self.quantity)

        self.row2.addWidget(self.add_btn)
        self.row2.addWidget(self.del_btn)
        self.row2.addStretch()
        self.row2.addWidget(QLabel("Subtotal:"))
        self.row2.addWidget(self.subtotal)

        self.row3.addStretch()
        self.row3.addWidget(self.cancel_btn)
        self.row3.addWidget(self.bill_btn)

        self.master_layout.addLayout(self.row1)
        self.master_layout.addLayout(self.row2)
        self.master_layout.addWidget(self.table)
        self.master_layout.addLayout(self.row3)

        self.setLayout(self.master_layout)

    def set_product_list(self):
        query = QSqlQuery("SELECT DISTINCT ProductName FROM Product")
        products = []
        while query.next():
            products.append(query.value(0))
        return products
    
    def add_product(self):
        product_name = self.product_list.currentText()
        quantity = self.quantity.value()
        query1 = QSqlQuery()
        query1.prepare("SELECT * FROM Product WHERE ProductName = ?")
        query1.addBindValue(product_name)
        if query1.exec_():
            if query1.next():
                stock_level = query1.value(4)

                if stock_level < quantity:
                    QMessageBox.critical(self, "Error", "Not enough stock available")
                    self.quantity.setValue(1)
                    return
                
                query2 = QSqlQuery()
                query2.prepare("SELECT DiscountValue FROM Discount WHERE DiscountID = ?")
                query2.addBindValue(query1.value(7))
                query2.exec_()

                discount = 0.0
                if query2.next():
                    discount = float(query2.value(0))
                
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(product_name)) # Product Name 0
                self.table.setItem(row, 1, QTableWidgetItem(str(quantity))) # Quantity 1
                self.table.setItem(row, 2, QTableWidgetItem(str(query1.value(3)))) # Unit Price 2
                self.table.setItem(row, 3, QTableWidgetItem(str(query1.value(3) * quantity))) # Total Price 3
                self.table.setItem(row, 4, QTableWidgetItem(str(discount))) # Discount 4
                self.subtotal_amount += int((1 - discount / 100) * query1.value(3) * quantity)
                self.subtotal.setText(str(self.subtotal_amount))
                # QMessageBox.information(self, "Success", "Row added to the table")

                self.product_list.setCurrentIndex(0)
                self.quantity.setValue(1)
        else:
            QMessageBox.critical(self, "Error", "Error adding product, Invalid Product Name")

    def rem_product(self):
        row_id = self.table.currentRow()
        if row_id == -1:
            QMessageBox.warning(self, "No row selected", "Please select a row to delete")
            return

        confirm = QMessageBox.question(self, "Are you sure?", "Remove Product?", QMessageBox.Yes | QMessageBox.No)

        if confirm == QMessageBox.No:
            return
        
        quantity = int(self.table.item(row_id, 1).text())
        unit_price = float(self.table.item(row_id, 2).text())
        discount = float(self.table.item(row_id, 4).text())

        amount = (1 - discount / 100) * unit_price * quantity

        self.subtotal_amount -= int(amount)
        self.subtotal.setText(str(self.subtotal_amount))

        self.table.removeRow(row_id)
        
        QMessageBox.information(self, "Success", "Row removed from the table")

    def checkout(self):
        if self.subtotal_amount == 0:
            QMessageBox.warning(self, "Warning", "No products added to the bill")
            return
        
        payment_dialog = PaymentBox(self.subtotal_amount, self)
        payment_dialog.exec_()
        method, amount = payment_dialog.get_payment_details()

        if amount < self.subtotal_amount:
            QMessageBox.warning(self, "Warning", "Amount paid is less than the total amount")
            return

        dateTime = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")

        # Updation of Sales Relation
        query = QSqlQuery()
        query.prepare("""
                      INSERT INTO Sales (SaleDate, TotalAmount, PaymentMethod, AmountPaid, BalanceDue) 
                      VALUES (?, ?, ?, ?, ?)
                    """)
        query.addBindValue(dateTime)
        query.addBindValue(self.subtotal_amount)
        query.addBindValue(method)
        query.addBindValue(amount)
        query.addBindValue(amount - self.subtotal_amount)
        query.exec_()

        # Updation of SaleDetails Relation
        sales_id = query.lastInsertId()
        for i in range(self.table.rowCount()):
            product_name = self.table.item(i, 0).text()
            quantity = int(self.table.item(i, 1).text())
            unit_price = float(self.table.item(i, 2).text())
            
            query1 = QSqlQuery()
            query1.prepare("SELECT ProductID, StockLevel FROM Product WHERE ProductName = ?")
            query1.addBindValue(product_name)
            query1.exec_()
            query1.next()
            product_id = query1.value(0)
            stock_level = query1.value(1)
            stock_level -= quantity

            query2 = QSqlQuery()
            query2.prepare("SELECT DiscountID FROM Discount WHERE DiscountValue = ?")
            query2.addBindValue(float(self.table.item(i, 4).text()))
            query2.exec_()
            query2.next()
            discount_id = query2.value(0)

            query3 = QSqlQuery()
            query3.prepare("""
                          INSERT INTO SaleDetails (SalesID, ProductID, Quantity, UnitPrice, Subtotal, DiscountID) 
                          VALUES (?, ?, ?, ?, ?, ?)
                        """)
            query3.addBindValue(sales_id)
            query3.addBindValue(product_id)
            query3.addBindValue(quantity)
            query3.addBindValue(unit_price)
            query3.addBindValue(unit_price * quantity)
            query3.addBindValue(discount_id)
            query3.exec_()

            query4 = QSqlQuery()
            query4.prepare("UPDATE Product SET StockLevel = ? WHERE ProductID = ?")
            query4.addBindValue(stock_level)
            query4.addBindValue(product_id)
            query4.exec_()

        # Updation of Invoice Relation
        query4 = QSqlQuery()
        query4.prepare("""
                      INSERT INTO Invoices (SalesID, InvoiceDate, TotalAmount, AmountPaid, BalanceDue, PaymentMethod) 
                      VALUES (?, ?, ?, ?, ?, ?)
                    """)
        query4.addBindValue(sales_id)
        query4.addBindValue(dateTime)
        query4.addBindValue(self.subtotal_amount)
        query4.addBindValue(amount)
        query4.addBindValue(amount - self.subtotal_amount)
        query4.addBindValue(method)
        query4.exec_()

        cwd = os.getcwd()
        bills_directory = os.path.join(cwd, "Bills")
        try:
            os.makedirs(bills_directory, exist_ok=True)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create directory {bills_directory}: {str(e)}")
            return
        file_path = os.path.join(bills_directory, f"bill_{dateTime}.pdf")

        self.create_bill(file_path, dateTime[:10], dateTime[11:])
        QMessageBox.information(self, "Success", "Bill Checked Out")
        self.cancel()

    def cancel(self):
        self.product_list.setCurrentIndex(0)
        self.quantity.setValue(1)
        self.subtotal_amount = 0
        self.subtotal.setText(str(self.subtotal_amount))
        self.table.setRowCount(0)

    def create_bill(self, file_path, date, time):
        c = canvas.Canvas(file_path, pagesize=letter)
        width, height = letter  # Page dimensions: 612 x 792 points

        # Header Section
        y_position = height - 50  # Start near the top
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, y_position, "Company Inc.")
        y_position -= 20
        c.setFont("Helvetica", 12)
        c.drawString(50, y_position, "1234 Fake Street, Imaginary City, IC 56789")
        y_position -= 20
        c.drawString(50, y_position, f"Date: {date}")
        y_position -= 20
        c.drawString(50, y_position, f"Time: {time}")
        y_position -= 40

        # Table Header
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y_position, "Item No.")
        c.drawString(150, y_position, "Name")
        c.drawString(350, y_position, "Price")
        y_position -= 10
        c.line(50, y_position, 550, y_position)  # Draw a line under the header
        y_position -= 20

        # Table Items (Dynamic)
        c.setFont("Helvetica", 12)
        for row in range(self.table.rowCount()):
            item_number = str(row + 1)
            product_name = self.table.item(row, 0).text()
            total_price = self.table.item(row, 3).text()  # Total Price column

            c.drawString(50, y_position, item_number)
            c.drawString(150, y_position, product_name)
            c.drawString(350, y_position, f"${float(total_price):.2f}")
            y_position -= 20

            # Check if we need a new page
            if y_position < 50:
                c.showPage()
                y_position = height - 50
                c.setFont("Helvetica", 12)
        
        # Subtotal Section
        y_position -= 20
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y_position, f"Subtotal: ${self.subtotal_amount:.2f}")
        y_position -= 40

        # Encouraging Message
        c.setFont("Helvetica-Oblique", 12)
        c.drawString(50, y_position, "Visit us again!")

        # Finalize the PDF
        c.save()
        return

database = QSqlDatabase.addDatabase("QSQLITE")
database.setDatabaseName("sms.db")

if not database.open():
    QMessageBox.critical(None, "Error", "Could not open database")
    sys.exit(1)

if __name__ == "__main__":
    app = QApplication([])
    window = BillingPage()
    window.show()
    app.exec_()