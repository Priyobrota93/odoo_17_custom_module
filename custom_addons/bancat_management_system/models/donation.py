from odoo import fields, models, api
import logging

_logger = logging.getLogger(__name__)

class AccountAccount(models.Model):
    _inherit = 'account.account'

    donor_id = fields.Many2one('bancat.donor', string="Donor", ondelete='cascade')
