from odoo import fields, models, api

class RelationType(models.Model):
    _name = 'dms.relation.type'
    _description = 'Relation Types'

    name = fields.Char(string="Name", required=True)

