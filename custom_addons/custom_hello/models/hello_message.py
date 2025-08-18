# -*- coding: utf-8 -*-
from odoo import models, fields

class HelloMessage(models.Model):
    _name = 'hello.message'
    _description = 'Hello Message'

    name = fields.Char(string='Message', required=True)
