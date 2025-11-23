-- Optional DROP-FOREIGN-KEY-CONSTRAINT-stage (only if you really need them)
ALTER TABLE IF EXISTS adventureworkslite_dbo.orderitems
    DROP CONSTRAINT IF EXISTS fk_orderitems_orders_1157579162;
ALTER TABLE IF EXISTS adventureworkslite_dbo.orderitems
    DROP CONSTRAINT IF EXISTS fk_orderitems_products_1173579219;
ALTER TABLE IF EXISTS adventureworkslite_dbo.orders
    DROP CONSTRAINT IF EXISTS fk_orders_customers_1109578991;

-- CREATE-CONSTRAINT-stage
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

-- CREATE-FOREIGN-KEY-CONSTRAINT-stage
ALTER TABLE adventureworkslite_dbo.orderitems
    ADD CONSTRAINT fk_orderitems_orders_1157579162
    FOREIGN KEY (orderid)
    REFERENCES adventureworkslite_dbo.orders (orderid)
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;

ALTER TABLE adventureworkslite_dbo.orderitems
    ADD CONSTRAINT fk_orderitems_products_1173579219
    FOREIGN KEY (productid)
    REFERENCES adventureworkslite_dbo.products (productid)
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;

ALTER TABLE adventureworkslite_dbo.orders
    ADD CONSTRAINT fk_orders_customers_1109578991
    FOREIGN KEY (customerid)
    REFERENCES adventureworkslite_dbo.customers (customerid)
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;
