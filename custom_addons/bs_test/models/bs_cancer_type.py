
from odoo import fields, models, api

class CancerType(models.Model):
    _name = 'bs.cancer.type'
    _description = 'Cancer Types'
    _rec_name = 'bs_name'

    bs_name = fields.Char(string="Name", required=True)
