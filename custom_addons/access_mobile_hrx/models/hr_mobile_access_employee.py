from odoo import fields, models, api
from odoo.exceptions import ValidationError
import hashlib

class TestPortalAccess(models.Model):
    _inherit = 'hr.employee'

    mobile_access = fields.Boolean(string='Mobile Access', default=False)
    password = fields.Char(string='Password')
    # email_sent = fields.Boolean(string='Email Sent', default=False)

    # def write(self, vals):
    #     if 'mobile_access' in vals and vals['mobile_access'] and not self.email_sent:
    #         try:
    #             template = self.env.ref('access_mobile_hrx.email_template_mobile_access')
    #             if not template:
    #                 raise ValidationError("Email template not found!")
    #             template.send_mail(self.id, force_send=True)
    #             vals['email_sent'] = True
    #         except Exception as e:
    #             raise ValidationError(f"Error sending email: {str(e)}")
    #     return super(TestPortalAccess, self).write(vals)

    def action_change_password(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Change Password',
            'res_model': 'hr.employee.change.password',
            'view_mode': 'form',
            'view_id': self.env.ref('access_mobile_hrx.view_change_password_form').id,
            'target': 'new',
            'context': {'default_employee_id': self.id}
        }


class HrEmployeeChangePassword(models.TransientModel):
    _name = 'hr.employee.change.password'
    _description = 'Change Password'

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    new_password = fields.Char(string='New Password', required=True)
    confirm_password = fields.Char(string='Confirm Password', required=True)

    @api.constrains('new_password', 'confirm_password')
    def _check_passwords(self):
        for record in self:
            if record.new_password != record.confirm_password:
                raise ValidationError("The new password and confirmation password do not match.")

    def _hash_password(self, password):
        employee = self.employee_id
        salt = f"{employee.name}{employee.id}".encode('utf-8')
        hashed_password = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, 600000)
        return hashed_password.hex()

    def action_set_password(self):
        self.ensure_one()
        employee = self.employee_id
        password_hash = self._hash_password(self.new_password)
        employee.password = password_hash
