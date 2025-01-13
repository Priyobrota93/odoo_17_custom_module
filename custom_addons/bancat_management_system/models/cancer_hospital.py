from odoo import models, fields, api

class BancatHospital(models.Model):
    _name = 'bancat.hospital'
    _description = 'Hospital'

    name = fields.Char(string='Hospital Name', required=True)
    address = fields.Text(string='Address')

    @api.onchange('current_hospital')
    def _onchange_current_hospital(self):
        # automatically set the current hospital if it's selected
        if self.current_hospital:
            self.current_hospital = self.current_hospital.id
            self.address = self.current_hospital.address