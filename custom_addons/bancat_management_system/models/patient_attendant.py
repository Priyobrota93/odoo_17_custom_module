from odoo import models, fields,api
from odoo.exceptions import ValidationError


class Attendance(models.Model):
    _name = 'bancat.attendance'
    _description = 'Patient Attendance'

    patient_id = fields.Many2one('bancat.patient', string='Patient', ondelete='cascade')
    atten_name = fields.Char(string='Name', required=True)
    atten_age = fields.Integer(string='Age', required=True, default=0)
    atten_gender = fields.Selection([
        ('', 'Select Gender'),
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ], string='Gender', required=True)
    atten_relation_of_patient = fields.Char(string='Relation of Patient', required=True)
    atten_profession = fields.Char(string='Profession')
    atten_address = fields.Text(string='Address')
    atten_contact_number = fields.Char(string='Contact Number', required=True)
    atten_education_level = fields.Char(string='Education Level')
    atten_reference = fields.Char(string='Reference')

    atten2_name = fields.Char(string='Name')
    atten2_age = fields.Integer(string='Age', default=0)
    atten2_gender = fields.Selection([
        ('', 'Select Gender'),
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ], string='Gender')
    atten2_relation_of_patient = fields.Char(string='Relation of Patient')
    atten2_profession = fields.Char(string='Profession')
    atten2_address = fields.Text(string='Address')
    atten2_contact_number = fields.Char(string='Contact Number')
    atten2_education_level = fields.Char(string='Education Level')
    atten2_reference = fields.Char(string='Reference')

    is_latest = fields.Boolean(string="Latest Attendant", default=True)

    @api.model
    def create(self, vals):
        patient_id = vals.get('patient_id')
        # Validation for primary attendant
        if not vals.get('atten_age') or vals['atten_age'] <= 0:
            raise ValidationError("The 'Age' field is mandatory and must be greater than 0.")

        # Validation for additional attendant
        if 'atten2_age' in vals and (not vals['atten2_age'] or vals['atten2_age'] <= 0):
            raise ValidationError("The 'Additional Age' field is mandatory and must be greater than 0.")

        if patient_id:
            self.env['bancat.attendance'].search([('patient_id', '=', patient_id)]).write({'is_latest': False})

        return super(Attendance, self).create(vals)


    def open_second_form(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Additional Attendant',
            'res_model': 'bancat.attendance',
            'res_id': self.id,  # Pass the current record's ID
            'view_mode': 'form',
            'view_id': self.env.ref('bancat_management_system.view_bancat_attendance_form_2').id,
            'target': 'new',
            'context': {'default_patient_id': self.patient_id.id}
        }


