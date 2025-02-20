from odoo import fields, models, api

class CancerType(models.Model):
    _name = 'bancat.cancer.type'
    _description = 'Cancer Types'

    name = fields.Char(string="Name", required=True)