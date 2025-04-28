from odoo import fields, models,api

class PatientVisit(models.Model):
    _name = 'bancat.patient.visit'
    _description = 'Patient Visit Information'

    patient_id = fields.Many2one('bancat.patient', string="Patient", required=True, ondelete='cascade')
    state = fields.Selection([
        ('check_in', 'Check In'),
        ('check_out', 'Check Out'),
    ], string="Stage", default='check_in', tracking=True)
    approximate_amount = fields.Float(string="Approximate Amount")

    start_date = fields.Datetime(string="Start Date", default=fields.Datetime.now, readonly=True)
    end_date = fields.Datetime(string="End Date")

    cancer_type = fields.Many2one('bancat.cancer.type', string="Cancer Type", store=True)
    cancer_stage = fields.Selection([
        ('', 'Select Cancer Stage'),
        ('stage_1', 'Stage I'),
        ('stage_2', 'Stage II'),
        ('stage_3', 'Stage III'),
        ('stage_4', 'Stage IV'),
    ], string="Cancer Stage", store=True)
    # cancer_stage = fields.Selection(related='patient_id.cancer_stage', string="Cancer Stage", store=True)
    current_hospital = fields.Many2one('bancat.hospital', string="Current Hospital", store=True)
    treatment_details = fields.Text(string="Treatment Details", store=True)
    # current_status = fields.Selection(related='patient_id.current_status', string="Current Status", store=True)

    current_status = fields.Selection([
        ('', 'Select Status'),
        ('under_treatment', 'Under Treatment'),
        ('recovered', 'Recovered'),
        ('critical', 'Critical'),
        ('discharged', 'Discharged'),
        ('deceased', 'Deceased'),
    ], string="Current Status", default='under_treatment', store=True)

    bed_allocation_id = fields.Many2one('bed.allocation', string="Bed Allocation", store=True)

    folder_id = fields.Many2one('documents.folder', string="Documents Folder")
    document_ids = fields.One2many('documents.document', 'visit_id', string="Visit Documents")
    #
    # document_count = fields.Integer(compute="_compute_document_count", string="Documents")
    #
    # @api.depends('folder_id')
    # def _compute_document_count(self):
    #     for visit in self:
    #         if visit.folder_id:
    #             count = self.env['documents.document'].search_count([
    #                 ('folder_id', '=', visit.folder_id.id)
    #             ])
    #             visit.document_count = count
    #         else:
    #             visit.document_count = 0
    #

    #

    # When a visit is created, copy the current data from the patient
    @api.model
    def create(self, vals):
        if vals.get('patient_id') and not vals.get('cancer_type'):
            patient = self.env['bancat.patient'].browse(vals['patient_id'])
            if patient:
                # Copy all relevant fields from the patient
                vals.update({
                    'cancer_type': patient.cancer_type.id if patient.cancer_type else False,
                    'cancer_stage': patient.cancer_stage,
                    'current_hospital': patient.current_hospital.id if patient.current_hospital else False,
                    'treatment_details': patient.treatment_details,
                    'current_status': patient.current_status,
                    'bed_allocation_id': patient.bed_allocation_id.id if patient.bed_allocation_id else False,
                })
        return super(PatientVisit, self).create(vals)