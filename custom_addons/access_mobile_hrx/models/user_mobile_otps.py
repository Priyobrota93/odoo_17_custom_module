from odoo import models, fields, api
from odoo.exceptions import ValidationError
import psycopg2
from psycopg2 import connect, OperationalError, Error as PsycopgError
import logging

_logger = logging.getLogger(__name__)

class HrAttendance(models.Model):
    _name = "hr.user.mobile_otps"

    username = fields.Char(string='User Name',required=True, index=True, copy=False )
    otp = fields.Char(string='OTP', required=True)
    expires_at = fields.Datetime(string='Expiration Time')