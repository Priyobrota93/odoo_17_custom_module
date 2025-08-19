from odoo import fields, models, api,SUPERUSER_ID
from datetime import date
import re
from odoo.exceptions import UserError


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
    age = fields.Integer(string="Age", compute="_compute_age", store=True, tracking=True)
    cancer_type = fields.Many2one("bancat.cancer.type", string="Cancer Type", tracking=True)  # ("model",string)
    cancer_stage = fields.Selection([
        ('', 'Select Cancer Stage'),
        ('stage_1', 'Stage I'),
        ('stage_2', 'Stage II'),
        ('stage_3', 'Stage III'),
        ('stage_4', 'Stage IV'),
    ], string="Cancer Stage", tracking=True)

    bed_allocation_id = fields.Many2one('bed.allocation', string="Bed Allocation", domain="[('is_available', '=', True)]", tracking=True)
    patient_address = fields.Char(string="Address",tracking=True)
    email = fields.Char(string="Email",tracking=True)
    emergency_contact=fields.Char(string="Emergency Contact",tracking=True)

    current_hospital = fields.Many2one('bancat.hospital', string="Current Hospital",tracking=True)
    hospital_address = fields.Text(string="Hospital Address", related="current_hospital.address", store=True, tracking=True)

    treatment_details = fields.Text(string="Treatment Details", tracking=True)
    current_status = fields.Selection([
        ('', 'Select Status'),
        ('under_treatment', 'Under Treatment'),
        ('recovered', 'Recovered'),
        ('critical', 'Critical'),
        ('discharged', 'Discharged'),
        ('deceased', 'Deceased'),
    ], string="Current Status", default='under_treatment', tracking=True)

    attendance_ids = fields.One2many('bancat.attendance', 'patient_id', string='Attendant Information', auto_join=True, tracking=True)

    document_ids = fields.One2many('documents.document', 'patient_id', string="Documents", copy=True)

    state = fields.Selection([
        ('check_in', 'Check In'),
        ('check_out', 'Check Out')
    ], string="State", default='check_in', tracking=True)
    approximate_amount = fields.Float(string="Approximate Amount", required=True, tracking=True)
    start_date = fields.Datetime(string="Start Date", related='create_date', default=fields.Datetime.now, readonly=True)
    end_date = fields.Datetime(string="End Date")

    visit_ids = fields.One2many('bancat.patient.visit', 'patient_id', string="Visits")

    latest_folder_id = fields.Many2one('documents.folder', string="Latest Document Folder",
                                       compute="_compute_latest_folder_id", store=True)
    document_count = fields.Integer(compute="_compute_document_count", string="Document Count")

    last_visit_state = fields.Selection([
        ('check_in', 'Check In'),
        ('check_out', 'Check Out'),
    ], string="Visit State", compute="_compute_last_visit_state", store=True, tracking=True)

    # Store previous data for check-in/check-out
    previous_cancer_type_id = fields.Many2one("bancat.cancer.type", string="Previous Cancer Type", tracking=False)
    previous_cancer_stage = fields.Selection([
        ('', 'Select Cancer Stage'),
        ('stage_1', 'Stage I'),
        ('stage_2', 'Stage II'),
        ('stage_3', 'Stage III'),
        ('stage_4', 'Stage IV'),
    ], string="Previous Cancer Stage", tracking=False)
    previous_current_hospital_id = fields.Many2one('bancat.hospital', string="Previous Hospital", tracking=False)
    previous_current_status = fields.Selection([
        ('', 'Select Status'),
        ('under_treatment', 'Under Treatment'),
        ('recovered', 'Recovered'),
        ('critical', 'Critical'),
        ('discharged', 'Discharged'),
        ('deceased', 'Deceased'),
    ], string="Previous Status", tracking=False)
    previous_treatment_details = fields.Text(string="Previous Treatment Details", tracking=False)
    previous_bed_allocation_id = fields.Many2one('bed.allocation', string="Previous Bed Allocation", tracking=False)


    @api.depends('visit_ids.state', 'visit_ids.start_date')
    def _compute_last_visit_state(self):
        for patient in self:
            if patient.visit_ids:
                # Sort visits by start_date descending and get the state of the latest visit
                sorted_visits = patient.visit_ids.sorted(
                    key=lambda v: v.start_date or fields.Datetime.from_string('1900-01-01'), reverse=True)
                patient.last_visit_state = sorted_visits[0].state
            else:
                patient.last_visit_state = False

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
        if not vals.get('patient_id'):
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
        })

        # Mark the bed as unavailable after allocation
        if patient.bed_allocation_id:
            patient.bed_allocation_id.is_available = False

        return patient



    @api.depends('visit_ids.folder_id', 'visit_ids.start_date')
    def _compute_latest_folder_id(self):
        for patient in self:
            if patient.visit_ids:
                # Get the most recent visit with a folder
                latest_visit = patient.visit_ids.filtered(lambda v: v.folder_id).sorted(
                    key=lambda v: v.start_date or fields.Datetime.from_string('1900-01-01'),
                    reverse=True
                )
                patient.latest_folder_id = latest_visit[0].folder_id if latest_visit else False
            else:
                patient.latest_folder_id = False


    @api.depends('latest_folder_id')
    def _compute_document_count(self):
        for patient in self:
            if patient.latest_folder_id:
                count = self.env['documents.document'].search_count([
                    ('folder_id', '=', patient.latest_folder_id.id)
                ])
                patient.document_count = count
            else:
                patient.document_count = 0

    def action_open_documents(self):
        self.ensure_one()

        # Find or create the folder for this patient
        folder = self._get_or_create_patient_folder()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Patient Documents',
            'res_model': 'documents.document',
            'view_mode': 'kanban,tree,form',
            'domain': [('folder_id', 'child_of', folder.id)],
            'context': {
                'default_patient_id': self.id,
                'default_folder_id': self.latest_folder_id.id if self.latest_folder_id else folder.id,
                'searchpanel_default_folder_id': folder.id,
            },
        }

    def _get_or_create_patient_folder(self):
        """Get or create a folder for this patient"""
        # Find or create the root documents folder
        documents_folder = self.env['documents.folder'].search([('name', '=', 'Patient Documents')], limit=1)
        if not documents_folder:
            documents_folder = self.env['documents.folder'].create({
                'name': 'Patient Documents',
                'description': 'Root folder for all patient documents',
            })

        # Find or create a subfolder for this patient
        patient_folder_name = f"{self.name}_{self.patient_id}"
        patient_folder = self.env['documents.folder'].search([
            ('name', '=', patient_folder_name),
            ('parent_folder_id', '=', documents_folder.id)
        ], limit=1)

        if not patient_folder:
            patient_folder = self.env['documents.folder'].create({
                'name': patient_folder_name,
                'description': f"Folder for patient {self.name}",
                'parent_folder_id': documents_folder.id,
            })

        return patient_folder

    def action_check_in(self):
        self.ensure_one()
        now = fields.Datetime.now()
        formatted_date = now.strftime('%Y-%m-%d')

        # Get the patient folder
        patient_folder = self._get_or_create_patient_folder()

        # Count existing visit folders for this patient to determine the next visit number
        existing_visit_folders = self.env['documents.folder'].search([
            ('parent_folder_id', '=', patient_folder.id),
            ('name', 'like', 'Visit_%'),
        ])
        visit_number = len(existing_visit_folders) + 1

        # Create a subfolder for this visit
        visit_folder_name = f"Visit_{visit_number}_{formatted_date}"
        visit_folder = self.env['documents.folder'].create({
            'name': visit_folder_name,
            'description': f"Visit on {formatted_date}",
            'parent_folder_id': patient_folder.id,
        })

        # If no bed selected now, try to reuse previous one if available
        if not self.bed_allocation_id and self.previous_bed_allocation_id and self.previous_bed_allocation_id.is_available:
            self.write({'bed_allocation_id': self.previous_bed_allocation_id.id})
            # don't clear previous_* here; it’s useful for audit/history

        # Mark chosen bed as unavailable
        if self.bed_allocation_id:
            self.bed_allocation_id.is_available = False

        # Create a new visit record
        new_visit = self.env['bancat.patient.visit'].create({
            'patient_id': self.id,
            'state': 'check_in',
            'approximate_amount': self.approximate_amount,
            'folder_id': visit_folder.id,
            'start_date': now,
            'cancer_type': self.cancer_type.id if self.cancer_type else False,
            'cancer_stage': self.cancer_stage,
            'current_hospital': self.current_hospital.id if self.current_hospital else False,
            'treatment_details': self.treatment_details,
            'current_status': self.current_status,
            'bed_allocation_id': self.bed_allocation_id.id if self.bed_allocation_id else False,
        })

        # Update the patient record
        self.write({
            'state': 'check_in',
            'start_date': now,
            'end_date': False,
        })



        # If there are previous values stored, restore them
        if self.previous_cancer_type_id or self.previous_cancer_stage or self.previous_current_hospital_id or self.previous_treatment_details or self.previous_current_status:
            self.write({
                'cancer_type': self.previous_cancer_type_id.id if self.previous_cancer_type_id else False,
                'cancer_stage': self.previous_cancer_stage,
                'current_hospital': self.previous_current_hospital_id.id if self.previous_current_hospital_id else False,
                'treatment_details': self.previous_treatment_details,
                'current_status': self.previous_current_status,
                # Clear previous values after restoring
                'previous_cancer_type_id': False,
                'previous_cancer_stage': False,
                'previous_current_hospital_id': False,
                'previous_treatment_details': False,
                'previous_current_status': False,
            })


        # Refresh the latest folder
        self._compute_latest_folder_id()

        return True


    def action_check_out(self):

        self.ensure_one()
        now = fields.Datetime.now()

        self.write({
            'state': 'check_out',
            'end_date': now,

            'previous_cancer_type_id': self.cancer_type.id if self.cancer_type else False,
            'previous_cancer_stage': self.cancer_stage,
            'previous_current_hospital_id': self.current_hospital.id if self.current_hospital else False,
            'previous_treatment_details': self.treatment_details,
            'previous_current_status': self.current_status,
            'previous_bed_allocation_id': self.bed_allocation_id.id if self.bed_allocation_id else False,
        })

        # Create a final record in patient_visit with all data before clearing
        if self.visit_ids and any(v.state == 'check_in' for v in self.visit_ids):
            open_visits = self.visit_ids.filtered(lambda v: v.state == 'check_in')
            if open_visits:
                open_visits[-1].write({
                    'state': 'check_out',
                    'end_date': now,
                    'cancer_type': self.cancer_type.id if self.cancer_type else False,
                    'cancer_stage': self.cancer_stage,
                    'current_hospital': self.current_hospital.id if self.current_hospital else False,
                    'treatment_details': self.treatment_details,
                    'current_status': self.current_status,
                    'bed_allocation_id': self.bed_allocation_id.id if self.bed_allocation_id else False,
                })

        # Free up the bed
        if self.bed_allocation_id:
            self.bed_allocation_id.is_available = True

        # Clear the fields in UI (but keep the data in database through previous_* fields)
        self.write({
            'cancer_type': False,
            'cancer_stage': False,
            'current_hospital': False,
            'treatment_details': False,
            'current_status': False,
            'bed_allocation_id': False,
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

    def action_view_release_paper(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.report',
            'report_name': 'bancat_management_system.release_paper_template',
            'report_type': 'qweb-html',
            'report_file': 'bancat_management_system.release_paper_template',
            'name': 'Release Paper',
            'context': {'lang': self.env.context.get('lang')},
        }
