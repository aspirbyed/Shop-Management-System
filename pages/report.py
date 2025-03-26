# Import Modules
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QWidget, QHeaderView,\
    QLabel, QPushButton, QTableWidget, QMessageBox, QTableWidgetItem, QComboBox, QDialog,\
    QLineEdit, QDialogButtonBox, QSpinBox, QCalendarWidget
from PyQt5.QtSql import QSqlDatabase, QSqlQuery
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtGui import QIntValidator
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import os
import sys
from gen_report import SalesAnalyzer

class DailyReportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Date for Daily Report")
        self.setGeometry(300, 300, 400, 400)

        # Create layout
        layout = QVBoxLayout()

        # Add calendar widget for date selection
        self.calendar = QCalendarWidget(self)
        self.calendar.setGridVisible(True)
        layout.addWidget(self.calendar)

        # Add buttons for OK and Cancel
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK", self)
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Cancel", self)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def get_selected_date(self):
        """Return the selected date in 'YYYY-MM-DD' format."""
        selected_date = self.calendar.selectedDate()
        return selected_date.toString("yyyy-MM-dd")

class MonthlyReportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Month for Monthly Report")
        self.setGeometry(300, 300, 300, 200)

        # Create layout
        layout = QVBoxLayout()

        # Add month and year selection
        self.month_label = QLabel("Select Month:")
        self.month_combo = QComboBox(self)
        self.month_combo.addItems([
            "01 - January", "02 - February", "03 - March", "04 - April",
            "05 - May", "06 - June", "07 - July", "08 - August",
            "09 - September", "10 - October", "11 - November", "12 - December"
        ])
        layout.addWidget(self.month_label)
        layout.addWidget(self.month_combo)

        self.year_label = QLabel("Select Year:")
        self.year_spin = QSpinBox(self)
        self.year_spin.setRange(2000, 2100)
        self.year_spin.setValue(2025)  # Default to current year or a reasonable default
        layout.addWidget(self.year_label)
        layout.addWidget(self.year_spin)

        # Add buttons for OK and Cancel
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK", self)
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Cancel", self)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def get_selected_month(self):
        """Return the selected month in 'YYYY-MM' format."""
        month = self.month_combo.currentText()[:2]  # Extract the month number (e.g., "01")
        year = str(self.year_spin.value())
        return f"{year}-{month}"

class YearlyReportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Year for Yearly Report")
        self.setGeometry(300, 300, 300, 150)

        # Create layout
        layout = QVBoxLayout()

        # Add year selection
        self.year_label = QLabel("Select Year:")
        self.year_spin = QSpinBox(self)
        self.year_spin.setRange(2000, 2100)
        self.year_spin.setValue(2025)  # Default to current year or a reasonable default
        layout.addWidget(self.year_label)
        layout.addWidget(self.year_spin)

        # Add buttons for OK and Cancel
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK", self)
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Cancel", self)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def get_selected_year(self):
        """Return the selected year as a string."""
        return str(self.year_spin.value())

class ReportPage(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Report Page")
        self.setFixedWidth(200)
        self.setFixedHeight(200)

        self.daily_btn = QPushButton("Daily Report")
        self.monthly_btn = QPushButton("Monthly Report")
        self.yearly_btn = QPushButton("Yearly Report")

        self.daily_btn.clicked.connect(self.daily_report)
        self.monthly_btn.clicked.connect(self.monthly_report)
        self.yearly_btn.clicked.connect(self.yearly_report)

        self.master_layout = QVBoxLayout()
        self.row1 = QHBoxLayout()
        self.row2 = QHBoxLayout()
        self.row3 = QHBoxLayout()

        self.row1.addWidget(self.daily_btn)
        self.row2.addWidget(self.monthly_btn)
        self.row3.addWidget(self.yearly_btn)

        self.master_layout.addWidget(QLabel("Generate Report"))
        self.master_layout.addLayout(self.row1)
        self.master_layout.addLayout(self.row2)
        self.master_layout.addLayout(self.row3)
        self.setLayout(self.master_layout)
    
    def daily_report(self):
        # Show the date selection dialog
        dialog = DailyReportDialog(self)
        if dialog.exec_():  # If the user clicks OK
            target_date = dialog.get_selected_date()
            print(f"Selected date for daily report: {target_date}")
            analyzer = SalesAnalyzer(db_path="sms.db")
            analyzer.main(target_date, None, None, 'day')

    def monthly_report(self):
        # Show the month selection dialog
        dialog = MonthlyReportDialog(self)
        if dialog.exec_():  # If the user clicks OK
            target_month = dialog.get_selected_month()
            print(f"Selected month for monthly report: {target_month}")
            analyzer = SalesAnalyzer(db_path="sms.db")
            analyzer.main(None, target_month, None, 'month')

    def yearly_report(self):
        # Show the year selection dialog
        dialog = YearlyReportDialog(self)
        if dialog.exec_():  # If the user clicks OK
            target_year = dialog.get_selected_year()
            print(f"Selected year for yearly report: {target_year}")
            analyzer = SalesAnalyzer(db_path="sms.db")
            analyzer.main(None, None, target_year, 'year')

if __name__ == '__main__':
    app = QApplication([])
    window = ReportPage()
    window.show()
    sys.exit(app.exec_())