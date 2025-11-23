-- ------------ Write DROP-FOREIGN-KEY-CONSTRAINT-stage scripts -----------

ALTER TABLE adventureworkslite_dbo.orderitems DROP CONSTRAINT fk_orderitems_orders_1157579162;

ALTER TABLE adventureworkslite_dbo.orderitems DROP CONSTRAINT fk_orderitems_products_1173579219;

ALTER TABLE adventureworkslite_dbo.orders DROP CONSTRAINT fk_orders_customers_1109578991;

-- ------------ Write DROP-CONSTRAINT-stage scripts -----------

ALTER TABLE adventureworkslite_dbo.customers DROP CONSTRAINT pk__customer__a4ae64b8d065cc23;

ALTER TABLE adventureworkslite_dbo.customers DROP CONSTRAINT uq__customer__a9d1053478edb5bc;

ALTER TABLE adventureworkslite_dbo.orderitems DROP CONSTRAINT pk__orderite__57ed06a17925d51d;

ALTER TABLE adventureworkslite_dbo.orders DROP CONSTRAINT pk__orders__c3905baf5e0c8751;

ALTER TABLE adventureworkslite_dbo.products DROP CONSTRAINT pk__products__b40cc6ed68f3a579;

-- ------------ Write DROP-TABLE-stage scripts -----------

DROP TABLE IF EXISTS adventureworkslite_dbo.customers;

DROP TABLE IF EXISTS adventureworkslite_dbo.orderitems;

DROP TABLE IF EXISTS adventureworkslite_dbo.orders;

DROP TABLE IF EXISTS adventureworkslite_dbo.products;

-- ------------ Write CREATE-DATABASE-stage scripts -----------

CREATE SCHEMA IF NOT EXISTS adventureworkslite_dbo;

-- ------------ Write CREATE-TABLE-stage scripts -----------

CREATE TABLE adventureworkslite_dbo.customers(
    customerid INTEGER NOT NULL GENERATED ALWAYS AS IDENTITY,
    firstname VARCHAR(50) NOT NULL,
    lastname VARCHAR(50) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(20),
    createddate TIMESTAMP WITHOUT TIME ZONE DEFAULT clock_timestamp(),
    modifieddate TIMESTAMP WITHOUT TIME ZONE DEFAULT clock_timestamp()
)
        WITH (
        OIDS=FALSE
        );

CREATE TABLE adventureworkslite_dbo.orderitems(
    orderitemid INTEGER NOT NULL GENERATED ALWAYS AS IDENTITY,
    orderid INTEGER NOT NULL,
    productid INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    unitprice NUMERIC(19,4) NOT NULL
)
        WITH (
        OIDS=FALSE
        );

CREATE TABLE adventureworkslite_dbo.orders(
    orderid INTEGER NOT NULL GENERATED ALWAYS AS IDENTITY,
    customerid INTEGER NOT NULL,
    orderdate TIMESTAMP WITHOUT TIME ZONE DEFAULT clock_timestamp(),
    totalamount NUMERIC(19,4),
    status VARCHAR(20) DEFAULT 'Pending'
)
        WITH (
        OIDS=FALSE
        );

CREATE TABLE adventureworkslite_dbo.products(
    productid INTEGER NOT NULL GENERATED ALWAYS AS IDENTITY,
    productname VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    price NUMERIC(19,4) NOT NULL,
    stockquantity INTEGER DEFAULT (0),
    createddate TIMESTAMP WITHOUT TIME ZONE DEFAULT clock_timestamp()
)
        WITH (
        OIDS=FALSE
        );

-- ------------ Write CREATE-CONSTRAINT-stage scripts -----------

ALTER TABLE adventureworkslite_dbo.customers
ADD CONSTRAINT pk__customer__a4ae64b8d065cc23 PRIMARY KEY (customerid);

ALTER TABLE adventureworkslite_dbo.customers
ADD CONSTRAINT uq__customer__a9d1053478edb5bc UNIQUE (email);

ALTER TABLE adventureworkslite_dbo.orderitems
ADD CONSTRAINT pk__orderite__57ed06a17925d51d PRIMARY KEY (orderitemid);

ALTER TABLE adventureworkslite_dbo.orders
ADD CONSTRAINT pk__orders__c3905baf5e0c8751 PRIMARY KEY (orderid);

ALTER TABLE adventureworkslite_dbo.products
ADD CONSTRAINT pk__products__b40cc6ed68f3a579 PRIMARY KEY (productid);

-- ------------ Write CREATE-FOREIGN-KEY-CONSTRAINT-stage scripts -----------

ALTER TABLE adventureworkslite_dbo.orderitems
ADD CONSTRAINT fk_orderitems_orders_1157579162 FOREIGN KEY (orderid) 
REFERENCES adventureworkslite_dbo.orders (orderid)
ON UPDATE NO ACTION
ON DELETE NO ACTION;

ALTER TABLE adventureworkslite_dbo.orderitems
ADD CONSTRAINT fk_orderitems_products_1173579219 FOREIGN KEY (productid) 
REFERENCES adventureworkslite_dbo.products (productid)
ON UPDATE NO ACTION
ON DELETE NO ACTION;

ALTER TABLE adventureworkslite_dbo.orders
ADD CONSTRAINT fk_orders_customers_1109578991 FOREIGN KEY (customerid) 
REFERENCES adventureworkslite_dbo.customers (customerid)
ON UPDATE NO ACTION
ON DELETE NO ACTION;

