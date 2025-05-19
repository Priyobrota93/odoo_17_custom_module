from odoo import models, fields, api, SUPERUSER_ID,_
from datetime import datetime
import logging,requests
from odoo.exceptions import ValidationError
from twilio.rest import Client


_logger = logging.getLogger(__name__)

class dms_inherit_contacts(models.Model):
    _inherit = 'res.partner'

    @api.model
    def send_birthday_wishes(self):
        today = datetime.today().strftime('%m-%d')
        template = self.env.ref('directory_management_system.email_template_birthday_wish', raise_if_not_found=False)
        if not template:
            _logger.warning("Birthday email template not found.")

        user = self.env.ref('base.user_admin')

        partners = self.search([('x_studio_birth_date', '!=', False)])
        for partner in partners:
            if partner.email and partner.x_studio_birth_date.strftime('%m-%d') == today:
                _logger.info(f"Sending birthday wish to {partner.name} ({partner.email})")
                template.with_user(user).send_mail(partner.id, force_send=True)

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

        partners = self.search([('x_studio_birth_date', '!=', False)])
        for partner in partners:
            try:
                if partner.mobile and partner.x_studio_birth_date.strftime('%m-%d') == today:
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



