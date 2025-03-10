from odoo import fields, models

class PatientVisit(models.Model):
    _name = 'bancat.patient.visit'
    _description = 'Patient Visit Information'

    patient_id = fields.Many2one('bancat.patient', string="Patient", required=True, ondelete='cascade')
    state = fields.Selection([
        ('check_in', 'Check In'),
        ('check_out', 'Check Out'),
    ], string="Stage", default='check_in', tracking=True)
    approximate_amount = fields.Float(string="Approximate Amount")
    start_date = fields.Datetime(string="Start Date", related='create_date', default=fields.Datetime.now, readonly=True)
    end_date = fields.Datetime(string="End Date")

    cancer_type = fields.Many2one('bancat.cancer.type', string="Cancer Type", related='patient_id.cancer_type',
                                  store=True)
    cancer_stage = fields.Selection(related='patient_id.cancer_stage', string="Cancer Stage", store=True)
    current_hospital = fields.Many2one('bancat.hospital', string="Current Hospital",
                                       related='patient_id.current_hospital', store=True)
    treatment_details = fields.Text(string="Treatment Details", related='patient_id.treatment_details', store=True)
