from odoo import models, fields, api, SUPERUSER_ID,_
from datetime import datetime
import logging,requests
from odoo.exceptions import ValidationError
from twilio.rest import Client
from datetime import date


_logger = logging.getLogger(__name__)

class dms_inherit_contacts(models.Model):
    _inherit = 'res.partner'

    x_studio_gender = fields.Selection(
        selection=[
            ('male', 'Male'),
            ('female', 'Female'),
            ('other', 'Other'),
        ],
        string="Gender",
        tracking=True
    )

    age = fields.Integer(string="Age", compute="_compute_age", store=True, tracking=True)
    birth_date = fields.Date(string="Date of Birth", required=True, tracking=True)
    religion = fields.Selection([
        ('', 'Select Religion'),
        ('hinduism', 'Hinduism'),
        ('islam', 'Islam'),
        ('christianity', 'Christianity'),
        ('buddhism', 'Buddhism'),
    ], string="Religion", store=True,  tracking=True)

    x_studio_relation = fields.Many2one("dms.relation.type", string = "Relation", store=True,  tracking=True)
    x_custom_name = fields.Char(string="Custom Name")

    @api.depends('birth_date')
    def _compute_age(self):
        for record in self:
            if record.birth_date:
                today = date.today()
                record.age = today.year - record.birth_date.year - (
                        (today.month, today.day) < (record.birth_date.month, record.birth_date.day)
                )
            else:
                record.age = 0

    def get_custom_name(self, name, religion, relationship):
        """Extracts formatted name based on religion and relationship."""
        name_parts = name.split()
        name_filtered = [part for part in name_parts if len(part) >= 3 and '.' not in part]
        first_valid = name_filtered[0] if name_filtered else name_parts[0]

        religion = (religion or '').strip().lower()
        relationship = (relationship or '').strip().lower()

        if relationship == 'sir':
            return f"{first_valid} Sir"
        elif relationship == 'colleague':
            return f"{first_valid} Bhai"
        elif relationship == 'friends':
            return f"{first_valid}"
        else:
            if religion == 'hinduism':
                return f"{first_valid} Dada"
            else:
                return f"{first_valid}"

    def _send_template_email(self, template, partner, user):
        customized_name = self.get_custom_name(
            partner.name,
            partner.religion,
            partner.x_studio_relation
        )
        _logger.info(f"Sending {template.name} to {partner.name} ({partner.email}) as {customized_name}")
        body = template.body_html
        if '{{custom_name}}' in body:
            body = body.replace('{{custom_name}}', customized_name)

        template.with_user(user).send_mail(partner.id, force_send=True, email_values={'body_html': body})

    def _get_today_str(self):
        return datetime.today().strftime('%m-%d')

    def _get_admin_user(self):
        return self.env.ref('base.user_admin')

    def _get_eligible_partners(self):
        return self.search([('email', '!=', False)])

    def _send_emails_for_fixed_date(self, expected_date, template_xml_id):
        today = self._get_today_str()
        if today != expected_date:
            return

        template = self.env.ref(template_xml_id, raise_if_not_found=False)
        if not template:
            return

        user = self._get_admin_user()
        partners = self._get_eligible_partners()

        for partner in partners:
            self._send_template_email(template, partner, user)

    def _send_birthday_emails(self, template_xml_id, date_field='birth_date'):
        today = self._get_today_str()
        template = self.env.ref(template_xml_id, raise_if_not_found=False)
        if not template:
            return

        user = self._get_admin_user()
        partners = self._get_eligible_partners()

        for partner in partners:
            bdate = getattr(partner, date_field, False)
            if not bdate or bdate.strftime('%m-%d') != today:
                continue
            self._send_template_email(template, partner, user)

    # 🎂 Birthday Scheduler
    @api.model
    def cron_send_birthday_emails(self):
        self._send_birthday_emails(
            'directory_management_system.email_template_role_base_birthday_wish'
        )

    # 📅 Pohela Boishakh
    @api.model
    def cron_send_pohela_boishakh_email(self):
        self._send_emails_for_fixed_date(
            '04-14',
            'directory_management_system.email_template_pohela_boishakh'
        )

    # 🕉️ Durga Puja
    @api.model
    def cron_send_durga_puja_email(self):
        self._send_emails_for_fixed_date(
            '10-20',
            'directory_management_system.email_template_durga_puja'
        )

    # 🕌 Eid-ul-Fitr
    @api.model
    def cron_send_eid_ul_fitr_email(self):
        self._send_emails_for_fixed_date(
            '04-10',
            'directory_management_system.email_template_eid_ul_fitr'
        )

    # 🐐 Eid-ul-Adha
    @api.model
    def cron_send_eid_ul_adha_email(self):
        self._send_emails_for_fixed_date(
            '05-25',
            'directory_management_system.email_template_eid_ul_adha'
        )

    # 🗣️ Language Day
    @api.model
    def cron_send_language_day_email(self):
        self._send_emails_for_fixed_date(
            '02-21',
            'directory_management_system.email_template_language_day'
        )

    # 🇧🇩 Independence Day
    @api.model
    def cron_send_independence_day_email(self):
        self._send_emails_for_fixed_date(
            '03-26',
            'directory_management_system.email_template_independence_day'
        )

    # 🏆 Victory Day
    @api.model
    def cron_send_victory_day_email(self):
        self._send_emails_for_fixed_date(
            '12-16',
            'directory_management_system.email_template_victory_day'
        )

    # 🎄 Christmas
    @api.model
    def cron_send_christmas_email(self):
        self._send_emails_for_fixed_date(
            '12-25',
            'directory_management_system.email_template_christmas'
        )

    # 🎉 New Year
    @api.model
    def cron_send_new_year_email(self):
        self._send_emails_for_fixed_date(
            '01-01',
            'directory_management_system.email_template_new_year'
        )

    # ☸️ Buddha Purnima
    @api.model
    def cron_send_buddha_purnima_email(self):
        self._send_emails_for_fixed_date(
            '05-23',
            'directory_management_system.email_template_buddha_purnima'
        )

    @api.model
    def send_birthday_sms(self):
        twilio_account = self.env['twilio.account'].search([('state', '=', 'confirm')], limit=1)
        if not twilio_account:
            raise ValidationError(_("No connected Twilio account found."))

        account_sid = twilio_account.account_sid
        auth_token = twilio_account.auth_token
        from_number = twilio_account.from_number

        if not account_sid or not auth_token or not from_number:
            raise ValidationError(_("Twilio credentials are not properly configured."))

        today = datetime.today().strftime('%m-%d')
        client = Client(account_sid, auth_token)

        partners = self.search([('birth_date', '!=', False)])
        for partner in partners:
            try:
                if partner.mobile and partner.birth_date.strftime('%m-%d') == today:
                    formatted_number = self.format_mobile_number(partner.mobile)

                    template =  """
                                    Hi {{ object.name }}, Happy Birthday!May this year bring you good health, happiness, and success.
                                """
                    message_body_dict = self.env['mail.render.mixin']._render_template_inline_template(
                        template,
                        'res.partner',
                        [partner.id]
                    )
                    message_body = message_body_dict[partner.id]

                    client.messages.create(
                        body=message_body,
                        from_=from_number,
                        to=formatted_number
                    )

                    _logger.info("Birthday SMS sent to %s (%s)", partner.name, formatted_number)

            except Exception as e:
                _logger.error("Failed to send SMS to %s: %s", partner.name, str(e))


    def format_mobile_number(self, number):
        number = number.strip().replace(' ', '').replace('-', '')

        if number.startswith('+'):
            return number  # Already valid

        if number.startswith('0') and len(number) == 11:
            return '+88' + number
        elif number.startswith('880') and len(number) == 13:
            return '+' + number
        elif len(number) == 10 and number.isdigit():
            return '+880' + number
        else:
            raise ValidationError("Invalid phone number format. Please use 017XXXXXXXX or +88017XXXXXXXX.")



