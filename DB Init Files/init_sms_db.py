import sqlite3
import csv

conn = sqlite3.connect('sms.db')
cursor = conn.cursor()

# with open('CSV Files/invoices.csv', 'r') as file:
#     csv_reader = csv.reader(file)
#     next(csv_reader)
#     for row in csv_reader:
#         cursor.execute('''
#             INSERT INTO Invoices (InvoiceID, SalesID, InvoiceDate, TotalAmount, AmountPaid, BalanceDue, PaymentMethod)
#             VALUES (?, ?, ?, ?, ?, ?, ?) ''', 
#             (int(row[0]), int(row[1]), row[2], float(row[3]), float(row[4]), float(row[5]), row[6]))

conn.commit()
conn.close()

print("Data copied successfully to table!")