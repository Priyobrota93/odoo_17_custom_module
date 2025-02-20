from odoo import fields, models, api

class ContributorType(models.Model):
    _name = 'bancat.contributor.type'
    _description = 'Contributo Types'

    name = fields.Char(string="Name", required=True)

    min_amount = fields.Float(required=True)

    max_amount = fields.Float(required=True)