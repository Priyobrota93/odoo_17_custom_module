import logging

from odoo import http
from odoo.http import request
from odoo.exceptions import ValidationError

from odoo.addons.payment_sslcommerz_ssl.commerz.payment import Validation


_logger = logging.getLogger(__name__)


class SSLCommerzController(http.Controller):
    _success_url = "/payment/sslcommerz/success"
    _fail_url = "/payment/sslcommerz/fail"
    _cancel_url = "/payment/sslcommerz/cancel"
    _ipn_url = "/payment/sslcommerz/ipn"

    @http.route(_success_url, type="http", auth="public", csrf=False)
    def sslcommerz_success(self, **data):
        """ Handle successful payment notification. """
        _logger.info("SSLCommerz Success Data: %s", data)
        try:
            tx = request.env["payment.transaction"].sudo(
            )._get_tx_from_notification_data('sslcommerz', data)
            tx._process_notification_data(data)

            # Redirect to a generic payment status page
            return request.redirect("/payment/status")
        except ValidationError as e:
            _logger.error(
                "Validation error handling SSLCommerz success: %s", e)
            return request.redirect("/payment/status?error=1")
        except Exception as e:
            _logger.exception("Error handling SSLCommerz success: %s", e)
            return request.redirect("/payment/status?error=1")

    @http.route(_fail_url, type="http", auth="public", csrf=False)
    def sslcommerz_fail(self, **data):
        """ Handle failed payment notification. """
        _logger.info("SSLCommerz Fail Data: %s", data)
        try:
            tx = request.env["payment.transaction"].sudo(
            )._get_tx_from_notification_data("sslcommerz", data)
            tx._set_error("Payment failed on SSLCommerz.")
            # Redirect to failure page
            return request.redirect("/payment/status?status=failed")
        except Exception as e:
            _logger.exception("Error handling SSLCommerz failure: %s", e)
            return request.redirect("/payment/status?error=1")

    @http.route(_cancel_url, type="http", auth="public", csrf=False)
    def sslcommerz_cancel(self, **data):
        """ Handle payment cancellation notification. """
        _logger.info("SSLCommerz Cancel Data: %s", data)
        try:
            tx = request.env["payment.transaction"].sudo(
            )._get_tx_from_notification_data("sslcommerz", data)
            tx._set_canceled()
            # Redirect to cancellation page
            return request.redirect("/payment/status?status=cancelled")
        except Exception as e:
            _logger.exception("Error handling SSLCommerz cancellation: %s", e)
            return request.redirect("/payment/status?error=1")

    @http.route(_ipn_url, type="http", auth="public", csrf=False)
    def sslcommerz_ipn(self, **data):
        """ Handle SSLCommerz IPN (Instant Payment Notification) """
        _logger.info("Received SSLCommerz IPN Data: %s", data)

        try:
            # Check the validity of the notification using signature verification
            provider = request.env["payment.provider"].sudo().search(
                [("code", "=", "sslcommerz")], limit=1)
            if not provider:
                _logger.error("No payment provider found for SSLCommerz.")
                return "FAIL"

            validation = Validation(
                sslc_is_sandbox=provider.state == 'test',
                sslc_store_id=provider.sslc_store_id,
                sslc_store_pass=provider.sslc_store_pass,
            )

            if not validation.validate_ipn_hash(data):
                _logger.error("Invalid IPN hash received for transaction: %s", data.get(
                    "tran_id", "Unknown"))
                return "FAIL"

            # Process the transaction using IPN data
            tx = request.env["payment.transaction"].sudo(
            )._get_tx_from_notification_data("sslcommerz", data)
            if not tx:
                _logger.error("Transaction not found for IPN data: %s",
                              data.get("tran_id", "Unknown"))
                return "FAIL"

            # Validate the transaction status with SSLCommerz
            result = validation.validate_transaction(data.get("val_id"))
            _logger.info("SSLCommerz Validation Result: %s", result)

            if result["status"] in ("VALIDATED", "VALID"):
                tx._set_done()
                _logger.info(
                    "Payment validated successfully for transaction: %s", tx.reference)
            elif result["status"] in ("FAILED", "DECLINED"):
                tx._set_error("Payment failed.")
                _logger.warning(
                    "Payment failed for transaction: %s", tx.reference)
            else:
                _logger.warning(
                    "Unexpected status received: %s", result["status"])
        except ValidationError as e:
            _logger.exception("Validation error during IPN processing: %s", e)
            return "FAIL"
        except Exception as e:
            _logger.exception("Error processing IPN: %s", e)
            return "FAIL"

        return "VALID"  # Acknowledge the IPN with 'VALID' to SSLCommerz
