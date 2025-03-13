from odoo import fields, models, api

class BSPatient(models.Model):
    _name='bs.patient'
    _description='bs patient information'

    def _valid_field_parameter(self, field, name):
        if name == 'unique':
            return True
        return super(BSPatient, self)._valid_field_parameter(field, name)

    bs_patient_id = fields.Char(string="Patient ID", unique=True)
    bs_name = fields.Char(string="Name", required=True)
    profile_image = fields.Binary(string="Profile Image", attachment=True)
    gender = fields.Selection([
        ('', 'Select Gender'),
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], string="Gender", required=True)
    dob = fields.Date(string="Date of Birth", required=True)
    age = fields.Integer(string="Age", compute="_compute_age", store=True)
    cancer_type = fields.Many2one("bs.cancer.type", string="Cancer Type", required=True, tracking=False)