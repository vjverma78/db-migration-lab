CREATE SCHEMA IF NOT EXISTS public;

CREATE OR REPLACE VIEW public.customers AS
SELECT *
FROM adventureworkslite_dbo.customers;

CREATE OR REPLACE VIEW public.orders AS
SELECT *
FROM adventureworkslite_dbo.orders;

CREATE OR REPLACE VIEW public.orderitems AS
SELECT *
FROM adventureworkslite_dbo.orderitems;

CREATE OR REPLACE VIEW public.products AS
SELECT *
FROM adventureworkslite_dbo.products;
