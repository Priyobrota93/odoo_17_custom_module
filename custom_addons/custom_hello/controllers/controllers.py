# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class HelloController(http.Controller):
    @http.route('/custom_hello/hello', type='http', auth='public', website=False)
    def hello(self, **kw):
        return "Hello from Custom Hello addon!"