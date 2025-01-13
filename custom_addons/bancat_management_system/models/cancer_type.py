from odoo import fields, models, api

class PropertyType(models.Model):
    _name = 'bancat.cancer.type'
    _description = 'Cancer Types'

    name = fields.Char(string="Name", required=True)