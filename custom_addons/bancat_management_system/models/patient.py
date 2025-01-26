from odoo import fields, models, api
from datetime import date


class Patient(models.Model):
    _name = 'bancat.patient'
    _description = 'Bancat patient Details'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _valid_field_parameter(self, field, name):
        # Allow the 'unique' parameter for fields
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
    # document_file = fields.Binary(string="Upload Document", attachment=True)
    # document_file_name = fields.Char(string="File Name")
    # atten_name = fields.Char(string='Attendance Name', required=True)
    # atten_relation_of_patient = fields.Char(string='Relation of Patient', required=True)
    # atten_address = fields.Text(string='Attendance Address')
    # atten_contact_number = fields.Char(string='Attendance Contact Number', required=True)
    #
    #
    # atten2_name = fields.Char(string='Attendance-2 Name')
    # atten2_relation_of_patient = fields.Char(string='Attendance-2 Relation of Patient')
    # atten2_address = fields.Text(string='Attendance-2 Address')
    # atten2_contact_number = fields.Char(string=' Attendance-2 Contact Number')


    # show_attendance_form2 = fields.Boolean(string="Show Attendance Form 2", default=False)

    # show_add_button = fields.Boolean(string="Show Add Button", default=True)

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
            if last_patient:
                # Extract the numeric part of the last patient_id and increment by 1
                last_patient_number = int(last_patient.patient_id.split("-")[-1])  # Assuming format like "PAT-1"
                new_patient_number = last_patient_number + 1
            else:
                # If no patient exists, start with 1
                new_patient_number = 1
            vals['patient_id'] = f'BANCAT-{new_patient_number}'  # Format as desired (e.g., BANCAT-1)

        return super(Patient, self).create(vals)

    @api.model
    def create(self, vals):
        # Generate patient_id if not provided
        if 'patient_id' not in vals or not vals['patient_id']:
            last_patient = self.search([], limit=1, order="patient_id desc")
            last_id = int(last_patient.patient_id.split("-")[-1]) if last_patient else 0
            vals['patient_id'] = f"BANCAT-{last_id + 1}"

        patient = super(Patient, self).create(vals)
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

    @api.model
    def create(self, vals):
        # Create a folder for the patient
        patient = super(Patient, self).create(vals)
        folder = self.env['documents.folder'].create({
            'name': patient.name,
            'description': f"Folder for patient {patient.name}",
        })
        patient.document_ids.write({'folder_id': folder.id})
        return patient