-- disable sslcommerz payment provider
UPDATE payment_provider
   SET sslc_store_id = NULL,
       sslc_store_pass = NULL;
