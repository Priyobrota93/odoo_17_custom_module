from odoo import models, fields, api
from odoo.exceptions import UserError

class HrAttendanceRequest(models.Model):
    _name = "hr.mobile.attendance.request"
    _description = "HR Mobile Attendance Request"
    _inherit = ["hr.attendance"]

    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    request_date = fields.Datetime(string="Request Date", default=fields.Datetime.now)
    check_in = fields.Datetime(string='Check In', required=True)
    check_out = fields.Datetime(string='Check Out', required=True)
    status = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], string='Status', default='draft', tracking=True)
    reason = fields.Text(string="Reason")
    attendance_id = fields.Many2one('hr.attendance', string="Attendance ID")

    @api.constrains('check_in', 'check_out')
    def _check_valid_dates(self):
        for record in self:
            if record.check_out and record.check_in and record.check_out <= record.check_in:
                raise UserError("Check-out time must be after check-in time.")

    # def calculate_worked_hours(self, check_in, check_out):
    #     if check_in and check_out:
    #         delta = check_out - check_in
    #         return delta.total_seconds() / 3600.0
    #     return 0.0

    def action_draft(self):
        self.write({'status': 'draft'})

    def action_approved(self):
        for record in self:
            if record.status != 'draft':
                raise UserError("Only draft requests can be approved.")
            if not record.check_in or not record.check_out:
                raise UserError("Check-in and Check-out times must be provided.")
            attendance_vals = {
                'employee_id': record.employee_id.id,
                'check_in': record.check_in,
                'check_out': record.check_out,
                # 'worked_hours': record.calculate_worked_hours(record.check_in, record.check_out),
                
            }
            if record.attendance_id:
                record.attendance_id.write(attendance_vals)
            else:
                record.attendance_id = self.env['hr.attendance'].create(attendance_vals)
            record.write({'status': 'approved'})

    def action_rejected(self):
        for record in self:
            if record.status != 'draft':
                raise UserError("Only draft requests can be rejected.")
            record.write({'status': 'rejected'})