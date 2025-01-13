from odoo import models, fields, api,_
from odoo.exceptions import ValidationError

import logging

_logger = logging.getLogger(__name__)

class ResPartnerInherit(models.Model):
    # _name = 'bsms.contact'
    _description = 'Contact for BSMS'
    _inherit = ["res.partner"]
    
    is_patient = fields.Boolean(string="Is Patient", default=False)
    is_donor = fields.Boolean(string="Is Donor", default=False)

    # channel_ids = fields.Many2many(comodel_name="mail.channel", string="Channels", compute=False, readonly=True)


    # channel_ids = fields.Many2many(
    #     comodel_name="mail.channel",
    #     relation="mail_channel_res_partner_rel",
    #     column1="partner_id",
    #     column2="channel_id",
    #     string="Channels",
    #     readonly=True
    # )


