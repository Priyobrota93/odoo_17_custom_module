from odoo import fields, models, api
from datetime import date
import re
from odoo.exceptions import ValidationError


class Donor(models.Model):
    _name = 'bancat.donor'
    _description = 'Bancat Donor Details'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _valid_field_parameter(self, field, name):
        if name == 'unique':
            return True
        return super(Donor, self)._valid_field_parameter(field, name)


    donor_id = fields.Char(string="Donor ID", unique=True, tracking=True)
    name = fields.Char(string="Name", required=True,tracking=True)
    profile_image = fields.Binary(string="Profile Image", attachment=True,tracking=False)
    gender = fields.Selection([
        ('', 'Select Gender'),
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], string="Gender", required=True, tracking=True)
    dob = fields.Date(string="Date of Birth", required=True, tracking=True)
    age = fields.Integer(string="Age", compute="_compute_age", store=True, tracking=True)
    donor_contact = fields.Char(string="Donor Contact", tracking=True)
    email = fields.Char(string="Email", tracking=True)
    donor_address = fields.Char(string="Address", tracking=True)
    donor_designation = fields.Char(string="Donor Designation", tracking=True)
    organization_name = fields.Char(string="Organization Name", tracking=True)
    donor_type = fields.Selection([
        ('individual', 'Individual'),
        ('organization', 'Organization'),
        ('anonymous', 'Anonymous'),
    ], default="individual", required=True, tracking=True)
    contact_name = fields.Char(string="Name", tracking=True)
    contact_designation = fields.Char(string="Designation", tracking=True)
    contact_contact = fields.Char(string="Contact", tracking=True)
    contact_email = fields.Char(string="Email", tracking=True)
    donor_tier = fields.Many2one('bancat.contributor.type', string="Donor Tier", required=True, tracking=True)
    donation_ids = fields.One2many('account.account', 'donor_id', string="Donations")




    @api.depends('dob')
    def _compute_age(self):
        for record in self:
            if record.dob:
                today = date.today()
                record.age = today.year - record.dob.year - (
                    (today.month, today.day) < (record.dob.month, record.dob.day)
                )
            else:
                record.age = 0

    @api.model
    def create(self, vals):
        # Generate donor_id if it's not provided
        if 'donor_id' not in vals or not vals['donor_id']:
            # Fetch the last donor ID used (to increment it)
            last_donor = self.search([], limit=1, order="donor_id desc")
            new_donor_number = 1  # Default if no previous donor exists

            if last_donor and last_donor.donor_id:
                match = re.search(r'(\d+)$', last_donor.donor_id)  # Extract only the number at the end
                if match:
                    new_donor_number = int(match.group(1)) + 1  # Convert extracted number to integer

            vals['donor_id'] = f'BANCAT-D{new_donor_number}'  # Format as desired (e.g., BANCAT-D1)

        return super(Donor, self).create(vals)

    @api.constrains('email', 'contact_email')
    def _check_email_format(self):
        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        for record in self:
            if record.email and not re.match(email_regex, record.email):
                raise ValidationError("Invalid email format for Donor Email: %s" % record.email)
            if record.contact_email and not re.match(email_regex, record.contact_email):
                raise ValidationError("Invalid email format for Contact Email: %s" % record.contact_email)