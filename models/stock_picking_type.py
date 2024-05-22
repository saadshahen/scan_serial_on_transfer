from odoo import models, fields

class CustomSaleOrder(models.Model):
    _inherit = "stock.picking.type"

    control_button = fields.Boolean(string='Import File')
