from odoo import fields, models, api
import logging

_logger = logging.getLogger(__name__)

class DocumentsDocument(models.Model):
    _inherit = 'documents.document'

    patient_id = fields.Many2one('bancat.patient', string="Patient", related='visit_id.patient_id', store=True, ondelete='cascade')
    visit_id = fields.Many2one('bancat.patient.visit', string="Visit", ondelete='cascade')

    # @api.model
    # def create(self, vals):
    #     # If there's binary data being passed directly, create attachment first
    #     if vals.get('attachment_binary') and not vals.get('attachment_id'):
    #         attachment_vals = {
    #             'name': vals.get('name', 'Attachment'),
    #             'datas': vals.pop('attachment_binary'),
    #             'res_model': 'documents.document',
    #         }
    #         attachment = self.env['ir.attachment'].create(attachment_vals)
    #         vals['attachment_id'] = attachment.id
    #
    #     return super(DocumentsDocument, self).create(vals)
