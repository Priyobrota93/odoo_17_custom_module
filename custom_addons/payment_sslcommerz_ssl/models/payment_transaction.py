import logging

from odoo import _, api, models
from odoo.exceptions import ValidationError

from odoo.addons.payment import utils as payment_utils
from odoo.addons.payment_sslcommerz_ssl.commerz.payment import SSLCSession, Validation


_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    @api.model
    def _compute_reference(self, provider_code, prefix=None, separator='-', **kwargs):
        """ Override of `payment` to ensure that SSLCommerz' requirements for references are satisfied.

        SSLCommerz' requirements for transaction are as follows:
        - References can only be made of alphanumeric characters and/or '-' and '_'.
          The prefix is generated with 'tx' as default. This prevents the prefix from being
          generated based on document names that may contain non-allowed characters
          (eg: INV/2020/...).

        :param str provider_code: The code of the provider handling the transaction.
        :param str prefix: The custom prefix used to compute the full reference.
        :param str separator: The custom separator used to separate the prefix from the suffix.
        :return: The unique reference for the transaction.
        :rtype: str
        """
        if provider_code == 'sslcommerz':
            prefix = payment_utils.singularize_reference_prefix()

        return super()._compute_reference(provider_code, prefix=prefix, separator=separator, **kwargs)

    def _get_specific_rendering_values(self, processing_values):
        """ Override of `payment` to return SSLCommerz-specific processing values.
        """
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'sslcommerz':
            return res

        provider = self.provider_id

        rendering_values = {
            'store_id': provider.sslc_store_id,
            'store_passwd': provider.sslc_store_pass,
            'tran_id': self.reference,
            'total_amount': self.amount,
            'currency': self.currency_id.name,
            'product_category': "E-commerce",
            'product_name': self.payment_method_id.name,
            'cus_name': self.partner_id.name,
            'cus_email': self.partner_id.email,
            'cus_add1': self.partner_id.contact_address,
            'cus_city': self.partner_id.city,
            'cust_postcode': self.partner_id.zip,
            'cust_country': self.partner_id.country_id.name,
            'cust_phone': self.partner_id.phone,
        }

        mypayment = SSLCSession(
            sslc_is_sandbox=provider.state == 'test',
            sslc_store_id=provider.sslc_store_id,
            sslc_store_pass=provider.sslc_store_pass,
        )

        urls = provider._get_urls()
        mypayment.set_urls(
            success_url=urls["success_url"],
            fail_url=urls["fail_url"],
            cancel_url=urls["cancel_url"],
            ipn_url=urls["ipn_url"]
        )

        mypayment.set_product_integration(
            tran_id=self.reference,
            total_amount=self.amount,
            currency=self.currency_id.name,
            product_category="E-commerce",
            product_name=self.payment_method_id.name,
            num_of_item=1,
            shipping_method="NO"
        )

        mypayment.set_customer_info(
            name=self.partner_id.name,
            email=self.partner_id.email,
            address1=self.partner_id.contact_address,
            city=self.partner_id.city,
            postcode=self.partner_id.zip,
            country=self.partner_id.country_id.name,
            phone=self.partner_id.phone,
        )

        response = mypayment.init_payment()
        _logger.info(response)
        if response["status"] == "SUCCESS":
            api_url = response["GatewayPageURL"]

            rendering_values.update({
                'api_url': api_url,
            })
            return rendering_values
        else:
            raise ValidationError(
                "Payment initialization failed: " + response.get("failedreason", "Unknown error"))

    def _get_tx_from_notification_data(self, provider_code, notification_data):
        """Find the transaction based on SSLCommerz data."""
        tx = super()._get_tx_from_notification_data(provider_code, notification_data)
        if provider_code != 'sslcommerz':
            return tx

        reference = notification_data.get("tran_id")
        if not reference:
            raise ValidationError(
                "Missing transaction reference in SSLCommerz response.")

        # Search for the transaction by reference
        tx = self.search([("reference", "=", reference),
                         ("provider_code", "=", provider_code)])
        if not tx:
            raise ValidationError(
                f"No transaction found matching reference {reference}.")
        return tx

    def _process_notification_data(self, notification_data):
        super()._process_notification_data(notification_data)
        if self.provider_code != 'sslcommerz':
            return

        _logger.info(
            f"Processing SSLCommerz notification data: {notification_data}")

        provider = self.provider_id

        # Update the provider reference.
        self.provider_reference = notification_data.get('tran_id')

        validation = Validation(
            sslc_is_sandbox=provider.state == 'test',
            sslc_store_id=provider.sslc_store_id,
            sslc_store_pass=provider.sslc_store_pass,
        )
        result = validation.validate_transaction(notification_data["val_id"])

        _logger.info(f"SSLCommerz Validation result: {result}")

        if result["status"] in ("VALIDATED", "VALID", "validated", "valid"):
            self._set_done()
        else:
            self._set_error(result["data"].get(
                "failedreason", "Unknown error"))
