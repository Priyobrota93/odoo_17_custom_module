from odoo import fields, models, api,SUPERUSER_ID
from datetime import date
import re


class Patient(models.Model):
    _name = 'bancat.patient'
    _description = 'Bancat patient Details'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _valid_field_parameter(self, field, name):
        if name == 'unique':
            return True
        return super(Patient, self)._valid_field_parameter(field, name)

    patient_id = fields.Char(string="Patient ID", unique=True, tracking=True)
    name = fields.Char(string="Name", required=True,tracking=True)
    profile_image = fields.Binary(string="Profile Image", attachment=True,tracking=False)
    gender = fields.Selection([
        ('', 'Select Gender'),
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], string="Gender", required=True,tracking=True)
    dob = fields.Date(string="Date of Birth",required=True,tracking=True)
    age = fields.Integer(string="Age", compute="_compute_age", store=True,tracking=True)
    cancer_type = fields.Many2one("bancat.cancer.type", string="Cancer Type", required=True,tracking=True)  # ("model",string)
    cancer_stage = fields.Selection([
        ('', 'Select Cancer Stage'),
        ('stage_1', 'Stage I'),
        ('stage_2', 'Stage II'),
        ('stage_3', 'Stage III'),
        ('stage_4', 'Stage IV'),
    ], string="Cancer Stage", required=True,tracking=True)

    bed_allocation_id = fields.Many2one('bed.allocation', string="Bed Allocation", domain="[('is_available', '=', True)]", tracking=True)
    patient_address = fields.Char(string="Address",tracking=True)
    email = fields.Char(string="Email",tracking=True)
    emergency_contact=fields.Char(string="Emergency Contact",tracking=True)

    current_hospital = fields.Many2one('bancat.hospital', string="Current Hospital",tracking=True)
    hospital_address = fields.Text(string="Hospital Address", related="current_hospital.address", store=True,tracking=True)

    treatment_details = fields.Text(string="Treatment Details",tracking=True)
    current_status = fields.Selection([
        ('under_treatment', 'Under Treatment'),
        ('recovered', 'Recovered'),
        ('critical', 'Critical'),
        ('discharged', 'Discharged'),
        ('deceased', 'Deceased'),
    ], string="Current Status", required=True, default='under_treatment',tracking=True)

    attendance_ids = fields.One2many('bancat.attendance', 'patient_id', string='Attendance Information', auto_join=True,tracking=True)
    document_ids = fields.One2many('documents.document', 'patient_id', string="Documents", copy=True)

    state = fields.Selection([
        ('check_in', 'Check In'),
        ('check_out', 'Check Out')
    ], string="State", default='check_in', tracking=True)
    approximate_amount = fields.Float(string="Approximate Amount")
    start_date = fields.Datetime(string="Start Date", related='create_date', default=fields.Datetime.now, readonly=True)
    end_date = fields.Datetime(string="End Date")

    # Link to visits (new model)
    visit_ids = fields.One2many('bancat.patient.visit', 'patient_id', string="Visits")


    last_visit_state = fields.Selection([
        ('check_in', 'Check In'),
        ('check_out', 'Check Out'),
    ], string="Visit State", compute="_compute_last_visit_state", store=True)

    @api.depends('visit_ids.state', 'visit_ids.start_date')
    def _compute_last_visit_state(self):
        for patient in self:
            if patient.visit_ids:
                # Sort visits by start_date descending and get the state of the latest visit
                sorted_visits = patient.visit_ids.sorted(
                    key=lambda v: v.start_date or fields.Datetime.from_string('1900-01-01'), reverse=True)
                patient.last_visit_state = sorted_visits[0].state
            else:
                patient.last_visit_state = False  # or set a default value like 'check_in'

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
        # Generate patient_id if it's not provided
        if 'patient_id' not in vals or not vals['patient_id']:
            # Fetch the last patient ID used (to increment it)
            last_patient = self.search([], limit=1, order="patient_id desc")
            new_patient_number = 1  # Default if no previous patient exists

            if last_patient and last_patient.patient_id:
                match = re.search(r'(\d+)$', last_patient.patient_id)  # Extract only the number at the end
                if match:
                    new_patient_number = int(match.group(1)) + 1  # Convert extracted number to integer

            vals['patient_id'] = f'BANCAT-D{new_patient_number}'  # Format as desired (e.g., BANCAT-D1)

        if 'state' not in vals:
            vals['state'] = 'check_in'

        patient = super(Patient, self).create(vals)

        self.env['bancat.patient.visit'].create({
            'patient_id': patient.id,
            'state': 'check_in',
            'start_date': fields.Datetime.now(),
            # Initialize other visit fields as needed...
        })

        # Mark the bed as unavailable after allocation
        if patient.bed_allocation_id:
            patient.bed_allocation_id.is_available = False
        return patient



    document_count = fields.Integer(compute="_compute_document_count", store=True)

    @api.depends('document_ids')
    def _compute_document_count(self):
        for record in self:
            record.document_count = len(record.document_ids)

    def action_open_documents(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Patient Documents',
            'res_model': 'documents.document',
            'view_mode': 'tree,form',
            'domain': [('patient_id', '=', self.id)],
            'context': {
                'default_patient_id': self.id,  # Set default patient when creating new documents
            },
        }
    # def action_check_out(self):
    #     self.ensure_one()
    #     return self.write({'state': 'check_out'})
    #
    # def write(self, vals):
    #     # Capture the state change if present
    #     res = super(Patient, self).write(vals)
    #     for record in self:
    #         # When state changes to check_out and end_date is not already set, capture the write_date as end_date
    #         if record.state == 'check_out' and not record.end_date:
    #             record.end_date = record.write_date
    #     return res

    def action_check_in(self):

        self.ensure_one()
        # Create a new visit record
        new_visit = self.env['bancat.patient.visit'].create({
            'patient_id': self.id,
            'state': 'check_in',
            'approximate_amount': self.approximate_amount,
            # start_date will be set automatically (default)
        })
        # Update the patient record
        self.write({
            'state': 'check_in',
            'start_date': fields.Datetime.now(),
            'end_date': False,
        })
        return True

    def action_check_out(self):

        self.ensure_one()
        now = fields.Datetime.now()
        self.write({
            'state': 'check_out',
            'end_date': now,
        })

        open_visits = self.visit_ids.filtered(lambda v: v.state == 'check_in')
        if open_visits:
            open_visits[-1].write({
                'state': 'check_out',
                'end_date': now,
            })
        return True

    def action_open_visit(self):

        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Patient Visits',
            'res_model': 'bancat.patient.visit',
            'view_mode': 'tree,form',
            # 'views': [(self.env.ref('bancat_management_system.bsms_patient_visit_tree_view').id, 'tree'), (False, 'form')],
            'domain': [('patient_id', '=', self.id)],
        }





    # @api.model
    # def create(self, vals):
    #     # Create a folder for the patient
    #     patient = super(Patient, self).create(vals)
    #     folder = self.env['documents.folder'].create({
    #         'name': patient.name,
    #         'description': f"Folder for patient {patient.name}",
    #     })
    #     patient.document_ids.write({'folder_id': folder.id})
    #     return patient