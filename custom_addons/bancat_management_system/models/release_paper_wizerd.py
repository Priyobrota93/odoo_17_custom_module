from odoo import fields, models, api


class PatientCheckoutWizard(models.TransientModel):
    _name = 'bancat.checkout.wizard'
    _description = 'Patient Checkout Wizard'

    patient_id = fields.Many2one('bancat.patient', string='Patient', required=True)

    # def action_print_release(self):
    #     self.ensure_one()
    #     return self.env.ref('bancat_management_system.action_report_patient_release').report_action(self.patient_id)
    #
    # def action_close(self):
    #     return {'type': 'ir.actions.act_window_close'}