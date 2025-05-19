import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class PaymentProvider(models.Model):
    _inherit = 'payment.provider'
    code = fields.Selection(
        selection_add=[('sslcommerz', "SSL Commerz Payment Gateway")], ondelete={'sslcommerz': 'set default'}
    )

    sslc_store_id = fields.Char(
        string="SSLCommerz Store ID", required_if_provider='sslcommerz',)
    sslc_store_pass = fields.Char(
        string="SSLCommerz Store Password", required_if_provider='sslcommerz',)

    def _get_urls(self):
        base_url = self.get_base_url()
        return {
            "success_url": f"{base_url}/payment/sslcommerz/success",
            "fail_url": f"{base_url}/payment/sslcommerz/fail",
            "cancel_url": f"{base_url}/payment/sslcommerz/cancel",
            "ipn_url": f"{base_url}/payment/sslcommerz/ipn",
        }

    def _get_default_payment_method_codes(self):
        if self.code == 'sslcommerz':
            return ['sslcommerz',]
        return super()._get_default_payment_method_codes()
