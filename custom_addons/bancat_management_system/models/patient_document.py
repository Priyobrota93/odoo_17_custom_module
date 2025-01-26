from odoo import fields, models, api
import logging

_logger = logging.getLogger(__name__)

class DocumentsDocument(models.Model):
    _inherit = 'documents.document'  # Inherit from the Documents module

    # Add a many2one field to link documents to the patient
    patient_id = fields.Many2one('bancat.patient', string="Patient", ondelete='cascade')
