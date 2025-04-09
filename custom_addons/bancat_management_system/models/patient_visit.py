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

    start_date = fields.Datetime(string="Start Date",   default=fields.Datetime.now, readonly=True)
    end_date = fields.Datetime(string="End Date")

    cancer_type = fields.Many2one('bancat.cancer.type', string="Cancer Type", related='patient_id.cancer_type',
                                  store=True)
    cancer_stage = fields.Selection(related='patient_id.cancer_stage', string="Cancer Stage", store=True)
    current_hospital = fields.Many2one('bancat.hospital', string="Current Hospital",
                                       related='patient_id.current_hospital', store=True)
    treatment_details = fields.Text(string="Treatment Details", related='patient_id.treatment_details', store=True)

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