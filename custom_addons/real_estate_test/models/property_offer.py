from odoo import fields, models, api
from datetime import timedelta

from odoo.exceptions import ValidationError


class PropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Estate Property Offer'

    name = fields.Char(string="Description", compute="_compute_name")
    price = fields.Float(string="Price")
    status = fields.Selection([('accepted', 'Accepted'), ('refused', 'Refused')], string="Status")
    partner_id = fields.Many2one('res.partner', string="Customer")
    property_id = fields.Many2one('estate.property', string="Property")
    validity = fields.Integer(string="Validity")
    deadline = fields.Date(string="Deadline",compute="_compute_deadline", inverse="_inverse_deadline")
    creation_date = fields.Date(string="Create Date")
    #
    # # _sql_constraints=[
    # #      ('check_validity','check(validity>0)','Deadline must be greater than creation date.')
    # # ]
    #
    # @api.model
    # def _set_create_date(self):
    #     return fields.Date.today()

    # creation_date = fields.Date(string="Create Date", default=_set_create_date)
    #
    @api.depends('validity', 'creation_date')
    # @api.depends_context('uid')
    def _compute_deadline(self):
        # print(self.env.context)
        # print(self._context)
        for record in self:
            if record.validity and record.creation_date:
                    record.deadline = (record.creation_date + timedelta(days=record.validity))
            else:
                record.deadline = False

    # def _inverse_deadline(self):
    #      for record in self:
    #           record.validity = (record.deadline - record.creation_date).days

    def _inverse_deadline(self):
        for record in self:
            if record.deadline and record.creation_date:
                record.validity = (record.deadline - record.creation_date).days
            else:
                record.validity = False

    @api.model_create_multi
    def create(self,values):
        for record in values:
              if not record.get('creation_date'):
                   record['creation_date'] = fields.Date.today()
        return super(PropertyOffer, self).create(values)
    #
    @api.constrains('validity')
    def _check_validity(self):
        for record in  self:
            if record.deadline <= record.creation_date:
                raise models.ValidationError('Deadline must be greater than creation date.')

    ############ORM Method practice start ########################

    # # def write(self, values):
    # #     print(values)
    # #     res_partner_ids = self.env['res.partner'].browse(10)
    # #     print(res_partner_ids.name)
    # #     return super(PropertyOffer,self).write(values)


    # def write(self, values):
    #     print(values)
    #     res_partner_ids = self.env['res.partner'].search_count([('is_company', '=', True)])
    #     print(res_partner_ids)
    #     return super(PropertyOffer,self).write(values)

    # def write(self, values):
    #     print(values)
    #     res_partner_ids = self.env['res.partner'].search([('is_company', '=', True)]).mapped('phone')
    #     print(res_partner_ids)
    #     return super(PropertyOffer,self).write(values)

    # def write(self, values):
    #     print(values)
    #     res_partner_ids = self.env['res.partner'].search([('is_company', '=', True)]).filtered(lambda x: x.phone =='(870)-931-0505')
    #     print(res_partner_ids)
    #     return super(PropertyOffer,self).write(values)

    ############ORM Method practice end ########################

    @api.depends('property_id', 'partner_id')
    def _compute_name(self):
        for record in self:
            if record.property_id and record.partner_id:
                record.name = f'{record.property_id.name} - {record.partner_id.name}'
            else:
                record.name = False
    #
    # def action_accept_offer(self):
    #     if self.property_id:
    #         self._validate_accepted_offer()
    #         self.property_id.write({
    #             'selling_price': self.price,
    #             'state': 'accepted'
    #
    #         })
    #     self.status = 'accepted'
    #
    # def _validate_accepted_offer(self):
    #     offer_ids = self.env['estate.property.offer'].search([
    #         ('property_id', '=', self.property_id.id),
    #         ('status', '=', 'accepted'),
    #     ])
    #     if offer_ids:
    #         raise ValidationError("you have an accepted offer already.")
    #
    # def action_decline_offer(self):
    #     self.status = 'refused'
    #     if all(self.property_id.offer_ids.mapped('status')):
    #         self.property_id.write({
    #             'selling_price': 0,
    #             'state': 'received'
    #
    #         })