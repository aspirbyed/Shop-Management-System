CREATE TABLE Discount (
    DiscountID INTEGER PRIMARY KEY AUTOINCREMENT,
    DiscountValue REAL NOT NULL
);

CREATE TABLE Category (
    CategoryID INTEGER PRIMARY KEY AUTOINCREMENT,
    CategoryName TEXT NOT NULL,
    AisleNumber TEXT NOT NULL
);

CREATE TABLE Sales (
    SalesID INTEGER PRIMARY KEY AUTOINCREMENT,
    SaleDate TEXT NOT NULL,
    TotalAmount REAL NOT NULL,
    PaymentMethod TEXT NOT NULL,
    AmountPaid REAL NOT NULL,
    BalanceDue REAL NOT NULL
);

CREATE TABLE Suppliers (
    SupplierID INTEGER PRIMARY KEY AUTOINCREMENT,
    SupplierName TEXT NOT NULL,
    ContactNumber TEXT,
    Address TEXT
);

CREATE TABLE Product (
    ProductID INTEGER PRIMARY KEY AUTOINCREMENT,
    ProductName TEXT NOT NULL,
    CategoryID INTEGER NOT NULL,
    Price REAL NOT NULL,
    StockLevel INTEGER NOT NULL,
    RestockLevel INTEGER NOT NULL,
    SupplierID INTEGER,
    DiscountID INTEGER DEFAULT 1 NOT NULL,
    FOREIGN KEY (CategoryID) REFERENCES Category(CategoryID),
    FOREIGN KEY (SupplierID) REFERENCES Suppliers(SupplierID),
    FOREIGN KEY (DiscountID) REFERENCES Discount(DiscountID)
);

CREATE TABLE InventoryTransactions (
    TransactionID INTEGER PRIMARY KEY AUTOINCREMENT,
    ProductID INTEGER NOT NULL,
    TransactionType TEXT NOT NULL,
    Quantity INTEGER NOT NULL,
    TransactionDate TEXT NOT NULL,
    SupplierID INTEGER NOT NULL,
    FOREIGN KEY (ProductID) REFERENCES Product(ProductID),
    FOREIGN KEY (SupplierID) REFERENCES Suppliers(SupplierID)
);

CREATE TABLE SaleDetails (
    SaleDetailID INTEGER PRIMARY KEY AUTOINCREMENT,
    SalesID INTEGER NOT NULL,
    ProductID INTEGER NOT NULL,
    Quantity INTEGER NOT NULL,
    UnitPrice REAL NOT NULL,
    Subtotal REAL NOT NULL,
    DiscountID INTEGER DEFAULT 1 NOT NULL,
    FOREIGN KEY (SalesID) REFERENCES Sales(SalesID),
    FOREIGN KEY (ProductID) REFERENCES Product(ProductID),
    FOREIGN KEY (DiscountID) REFERENCES Discount(DiscountID)
);

CREATE TABLE Invoices (
    InvoiceID INTEGER PRIMARY KEY AUTOINCREMENT,
    SalesID INTEGER NOT NULL,
    InvoiceDate TEXT NOT NULL,
    TotalAmount REAL NOT NULL,
    AmountPaid REAL NOT NULL,
    BalanceDue REAL NOT NULL,
    PaymentMethod TEXT NOT NULL,
    FOREIGN KEY (SalesID) REFERENCES Sales(SalesID)
);