from odoo import fields, models, api


class PropertyTag(models.Model):
    _name = 'estate.property.tag'
    _description = 'Property Tags'

    name = fields.Char(string="Name", required=True)
    color = fields.Integer(string="Color")