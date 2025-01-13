from odoo import fields, models, api


class Property(models.Model):
    _name = 'estate.property'
    _description = 'Estate Properties'

    name = fields.Char(string="Name", required=True)
    state = fields.Selection(
        [('new', 'New'),
         ('received', 'Offer Received'),
         ('accepted', 'Offer Accepted'),
          ('sold', 'Sold'),
         ('cancel', 'Cancelled')], default='new', string="Status")
    description = fields.Text(string="Description")
    postcode = fields.Char(string="Postcode")
    date_availability = fields.Date(string="Available Form")
    expected_price = fields.Float(string="Expected price")
    best_offer = fields.Float(string="Best Offer")
    selling_price = fields.Float(string="Selling price", readonly=True)
    bedrooms = fields.Integer(string="Bedrooms")
    leaving_area = fields.Integer(string="Leaving area (sqm)")
    facades = fields.Integer(string="Facades")
    garage = fields.Boolean(string="Garage", default=False)
    garden = fields.Boolean(string="Garden", default=False)
    garden_area = fields.Integer(string="Garden Area (sqm)")
    garden_orientation = fields.Selection([('north', 'North'), ('south', 'South'), ('east', 'East'), ('west', 'West')],
                                          string="Garden Orientation", default='north')
    type_id = fields.Many2one("estate.property.type", string="Property Type")  # ("model",string)
    tag_ids = fields.Many2many("estate.property.tag", string="Property Tag")  # ("model",string)
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")  # ("model",string)
    sales_id = fields.Many2one("res.users", string="Salesman")  # ("model",string)
    sales_phone = fields.Char(string="Sales Phone", related="sales_id.phone")
    buyer_id = fields.Many2one("res.partner", string="Buyer", domain=[('is_company', '=',
                                                                       True)])  # ("model",string) #domain = filter with fields with perticular model and pertcular setuation
    buyer_phone = fields.Char(string="Buyer Phone", related="buyer_id.phone")
    total_area = fields.Integer(string="Total Area (sqm)", compute="_compute_total_area")
    offer_count = fields.Integer(string="Offer Count", compute="_compute_offer_count")

    def action_sold(self):
        self.state = 'sold'

    def action_cancel(self):
        self.state = 'cancel'

    @api.depends('leaving_area', 'garden_area')
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.leaving_area + record.garden_area

#     @api.depends('offer_ids.price')
#     def _compute_best_offer(self):
#         for record in self:
#             record.best_offer = max(record.offer_ids.mapped('price'), default=0)
#
#     @api.depends('offer_ids')
#     def _compute_offer_count(self):
#         for record in self:
#             record.offer_count = len(record.offer_ids)
#
#     def action_property_offer_count_view(self):
#         return {
#             'type': 'ir.actions.act_window',
#             'name': f"{self.name} - Offers",
#             'domain': [('property_id', '=', self.ids)],
#             'view_mode': 'list',
#             'res_model': 'estate.property.offer',
#         }







