from odoo import models, fields, api

class BedAllocation(models.Model):
    _name = 'bed.allocation'
    _description = 'Bed Allocation'
    _rec_name = 'bed_display_name'

    building_name = fields.Selection([
        ('alok_nibash_1', 'Alok Nibash 1'),
        ('alok_nibash_2', 'Alok Nibash 2')
    ], string="Building Name", required=True)

    room_no = fields.Char(string="Room Number", required=True)
    bed_no = fields.Integer(string="Bed Number", required=True)
    is_available = fields.Boolean(string="Available", default=True)

    bed_display_name = fields.Char(
        string="Bed Name", compute="_compute_bed_display_name", store=True)

    @api.depends('building_name', 'room_no', 'bed_no')
    def _compute_bed_display_name(self):
        for record in self:
            record.bed_display_name = f"{record.building_name} - Room {record.room_no} - Bed {record.bed_no}"
