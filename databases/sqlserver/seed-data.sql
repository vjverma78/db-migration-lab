USE AdventureWorksLite;
GO

INSERT INTO Customers (FirstName, LastName, Email, Phone) VALUES
('John', 'Doe', 'john.doe@example.com', '555-0101'),
('Jane', 'Smith', 'jane.smith@example.com', '555-0102'),
('Bob', 'Johnson', 'bob.johnson@example.com', '555-0103'),
('Alice', 'Williams', 'alice.w@example.com', '555-0104'),
('Charlie', 'Brown', 'charlie.b@example.com', '555-0105');

INSERT INTO Products (ProductName, Category, Price, StockQuantity) VALUES
('Laptop', 'Electronics', 999.99, 50),
('Mouse', 'Accessories', 29.99, 200),
('Keyboard', 'Accessories', 79.99, 150),
('Monitor', 'Electronics', 299.99, 75),
('USB Cable', 'Accessories', 9.99, 500);

INSERT INTO Orders (CustomerID, OrderDate, TotalAmount, Status) VALUES
(1, GETDATE(), 1109.98, 'Completed'),
(2, GETDATE()-1, 339.98, 'Shipped'),
(3, GETDATE()-2, 79.99, 'Pending'),
(1, GETDATE()-3, 299.99, 'Completed'),
(4, GETDATE()-1, 1029.98, 'Processing');

INSERT INTO OrderItems (OrderID, ProductID, Quantity, UnitPrice) VALUES
(1, 1, 1, 999.99),
(1, 3, 1, 79.99),
(1, 2, 1, 29.99),
(2, 4, 1, 299.99),
(2, 5, 4, 9.99);
GO
