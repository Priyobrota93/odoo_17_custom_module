# Odoo module for SSLCOMMERZ

## Description

This module integrates SSLCommerz Payment Gateway using the generic payment with redirection flow based
on form submission provided by the `payment` module.

## Supported features

- Payment with redirection flow
- Instant Payment Notification(IPN)

## Prerequisite

- Odoo 16 or higher
- A <a href="https://developer.sslcommerz.com/registration/" target="_blank">Sandbox Account</a>  or <a href="https://join.sslcommerz.com/" target="_blank">Live Merchant Account</a>

## Installation instructions

Please Follow these steps for setting up SSLCommerz Payment module in Odoo.
- Download or clone the repository
- Unzip and move the payment_sslcommerz_ssl folder in your Odoo module directory
- Go Odoo settings and activate the developer mode and click on Update app list
- Search for Payment Provider: SSLCommerz
- Activate the module

----------
![](/payment_sslcommerz_ssl/static/description/images/module_sslcommerz.png)

## Setup

Once you have installed the module please follow these steps for setting up SSLCommerz Payment Provider.
- Go to your websites Configuration > Payment Providers & select SSLCommerz
- Enter your credentials. For testing enter your sandbox store id and password and set the state as Test Mode. For production enter your merchant store id and password and set the state as Enabled.
- Now you will be able to select SSLCommerz payment method in the checkout page.

----------
![](/payment_sslcommerz_ssl/static/description/images/2_select_payment_method.png)


### Test Credit Card Account Numbers

VISA

    Card Number: 4111111111111111
    Exp: 12/25
    CVV: 111

Mastercard

    Card Number: 5111111111111111
    Exp: 12/25
    CVV: 111

American Express

    Card Number: 371111111111111
    Exp: 12/25
    CVV: 111

Mobile OTP

    111111 or 123456
    
### Test Mobile Banking

Just choose any of the Mobile Banking method.

For more information please visit: https://sslcommerz.com/integration-document/

© 2024 SSLCOMMERZ ALL RIGHTS RESERVED
