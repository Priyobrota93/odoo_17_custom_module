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
        ('', 'Select Status'),
        ('under_treatment', 'Under Treatment'),
        ('recovered', 'Recovered'),
        ('critical', 'Critical'),
        ('discharged', 'Discharged'),
        ('deceased', 'Deceased'),
    ], string="Current Status", required=True, default='under_treatment',tracking=True)

    attendance_ids = fields.One2many('bancat.attendance', 'patient_id', string='Attendant Information', auto_join=True,tracking=True)

    document_ids = fields.One2many('documents.document', 'patient_id', string="Documents", copy=True)

    state = fields.Selection([
        ('check_in', 'Check In'),
        ('check_out', 'Check Out')
    ], string="State", default='check_in', tracking=True)
    approximate_amount = fields.Float(string="Approximate Amount")
    start_date = fields.Datetime(string="Start Date", related='create_date', default=fields.Datetime.now, readonly=True)
    end_date = fields.Datetime(string="End Date")

    visit_ids = fields.One2many('bancat.patient.visit', 'patient_id', string="Visits")

    latest_folder_id = fields.Many2one('documents.folder', string="Latest Document Folder",
                                       compute="_compute_latest_folder_id", store=True)
    document_count = fields.Integer(compute="_compute_document_count", string="Document Count")
    latest_folder_document_count = fields.Integer(compute="_compute_latest_folder_document_count",
                                                  string="Latest Folder Documents")


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

        # Documents module with the format 'name_patient_id' and Assign the patient's documents
        # folder_name = f"{patient.name}_{patient.patient_id}"
        # folder = self.env['documents.folder'].create({
        #     'name': folder_name,
        #     'description': f"Folder for patient {patient.name} with ID {patient.patient_id}",
        # })
        #
        # patient.document_ids.write({'folder_id': folder.id})

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

    @api.depends('document_ids')
    def _compute_document_count(self):
        for patient in self:
            patient.document_count = len(patient.document_ids)

    @api.depends('latest_folder_id')
    def _compute_latest_folder_document_count(self):
        for patient in self:
            if patient.latest_folder_id:
                count = self.env['documents.document'].search_count([
                    ('folder_id', '=', patient.latest_folder_id.id)
                ])
                patient.latest_folder_document_count = count
            else:
                patient.latest_folder_document_count = 0

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

        # Create a new visit record
        new_visit = self.env['bancat.patient.visit'].create({
            'patient_id': self.id,
            'state': 'check_in',
            'approximate_amount': self.approximate_amount,
            'folder_id': visit_folder.id,
            'start_date': now,
        })

        # Update the patient record
        self.write({
            'state': 'check_in',
            'start_date': now,
            'end_date': False,
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


    # @api.depends('document_ids')
    # def _compute_document_count(self):
    #     for record in self:
    #         record.document_count = len(record.document_ids)

    # def action_open_documents(self):
    #     self.ensure_one()
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Patient Documents',
    #         'res_model': 'documents.document',
    #         'view_mode': 'tree,form',
    #         'domain': [('patient_id', '=', self.id)],
    #         'context': {
    #             'default_patient_id': self.id,  # Set default patient when creating new documents
    #         },
    #     }

    # def action_open_documents(self):
    #     self.ensure_one()
    #     current_visit = self.visit_ids.filtered(lambda v: v.state == 'check_in')
    #     domain = [('patient_id', '=', self.id)]  # Always filter by patient
    #     context = {
    #         'default_patient_id': self.id,
    #         # Default folder/visit for new documents if current visit exists
    #         'default_folder_id': current_visit.folder_id.id if current_visit else False,
    #         'default_visit_id': current_visit.id if current_visit else False,
    #     }
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Patient Documents',
    #         'res_model': 'documents.document',
    #         'view_mode': 'tree,form',
    #         'domain': domain,
    #         'context': context,
    #     }







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




    # def action_check_in(self):
    #
    #     self.ensure_one()
    #
    #     # Get the formatted date
    #     now = fields.Datetime.now()
    #     formatted_date = now.strftime('%Y-%m-%d')
    #
    #     # Create a folder in documents module
    #     parent_folder = self.env['documents.folder'].search([('name', '=', 'Patient Documents')], limit=1)
    #     if not parent_folder:
    #         parent_folder = self.env['documents.folder'].create({
    #             'name': 'Patient Documents',
    #             'description': 'Root folder for all patient documents',
    #         })
    #
    #     # Create a folder in documents module
    #     folder_name = f"{self.name}_{self.patient_id}/{formatted_date}"
    #     folder = self.env['documents.folder'].create({
    #         'name': folder_name,
    #         'description': f"Visit folder for patient {self.name} with ID {self.patient_id} on {formatted_date}",
    #         'parent_folder_id': parent_folder.id,
    #     })
    #
    #     # Create a new visit record
    #     new_visit = self.env['bancat.patient.visit'].create({
    #         'patient_id': self.id,
    #         'state': 'check_in',
    #         'approximate_amount': self.approximate_amount,
    #         'folder_id': folder.id,
    #         # start_date will be set automatically (default)
    #     })
    #
    #     # Store the folder ID in the visit record
    #     # First, add a folder_id field to the PatientVisit model
    #     if hasattr(new_visit, 'folder_id'):
    #         new_visit.folder_id = folder.id
    #
    #     # Update the patient record
    #     self.write({
    #         'state': 'check_in',
    #         'start_date': fields.Datetime.now(),
    #         'end_date': False,
    #     })
    #     return True







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