-- CREATE-DATABASE-stage
CREATE SCHEMA IF NOT EXISTS adventureworkslite_dbo;

-- CREATE-TABLE-stage
CREATE TABLE adventureworkslite_dbo.customers(
    customerid INTEGER NOT NULL GENERATED ALWAYS AS IDENTITY,
    firstname VARCHAR(50) NOT NULL,
    lastname VARCHAR(50) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(20),
    createddate TIMESTAMP WITHOUT TIME ZONE DEFAULT clock_timestamp(),
    modifieddate TIMESTAMP WITHOUT TIME ZONE DEFAULT clock_timestamp()
) WITH (OIDS=FALSE);

CREATE TABLE adventureworkslite_dbo.orderitems(
    orderitemid INTEGER NOT NULL GENERATED ALWAYS AS IDENTITY,
    orderid INTEGER NOT NULL,
    productid INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    unitprice NUMERIC(19,4) NOT NULL
) WITH (OIDS=FALSE);

CREATE TABLE adventureworkslite_dbo.orders(
    orderid INTEGER NOT NULL GENERATED ALWAYS AS IDENTITY,
    customerid INTEGER NOT NULL,
    orderdate TIMESTAMP WITHOUT TIME ZONE DEFAULT clock_timestamp(),
    totalamount NUMERIC(19,4),
    status VARCHAR(20) DEFAULT 'Pending'
) WITH (OIDS=FALSE);

CREATE TABLE adventureworkslite_dbo.products(
    productid INTEGER NOT NULL GENERATED ALWAYS AS IDENTITY,
    productname VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    price NUMERIC(19,4) NOT NULL,
    stockquantity INTEGER DEFAULT (0),
    createddate TIMESTAMP WITHOUT TIME ZONE DEFAULT clock_timestamp()
) WITH (OIDS=FALSE);
