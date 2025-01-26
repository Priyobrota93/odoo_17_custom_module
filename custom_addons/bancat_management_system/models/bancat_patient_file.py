from odoo import fields, models, api

class PatientFile(models.Model):
    _name = 'bancat.patient.file'
    _description = 'Bancat Patient File'
    # _inherit = 'documents.document'  # Inherit from the Documents module

    folder_name = fields.Char(string="Folder Name", required=False, help="Optional folder grouping")
    name = fields.Char(string="File Name", required=True)
    attachment_id = fields.Many2one('ir.attachment', string="Attachment", required=True)
    file_description = fields.Text(string="Description")

    # Add a many2one field to link documents to the patient
    # patient_id = fields.Many2one('bancat.patient', string="Patient", ondelete='cascade')