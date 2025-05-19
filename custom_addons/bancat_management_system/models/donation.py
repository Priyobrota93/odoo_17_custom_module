# from odoo import fields, models, api
# import logging
#
# _logger = logging.getLogger(__name__)
#
# class AccountAccount(models.Model):
#     _inherit = 'account.account'
#
#     donor_id = fields.Many2one('bancat.donor', string="Donor", ondelete='cascade')

from odoo import models, fields, api
from datetime import datetime

class Donation(models.Model):
    _name = 'bancat.donation'
    _description = 'Donation Record'

    donor_id = fields.Many2one('bancat.donor', string="Donor", required=True)
    amount = fields.Float(string="Donation Amount", required=True)
    date = fields.Date(string="Donation Date", default=fields.Date.today)
    method = fields.Selection([
        ('manual', 'Manual'),
        ('sslcommerz', 'SSLCommerz'),
    ], string="Method", required=True)
    status = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('failed', 'Failed'),
    ], default='draft', string="Status")

    note = fields.Text(string="Note")

    def action_pay_sslcommerz(self):
        for donation in self:
            # Your SSLCommerz integration logic goes here
            # This might include redirecting to a payment gateway
            donation.status = 'confirmed'  # Mark as confirmed after success

