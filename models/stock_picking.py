from odoo import models, fields

class CustomSaleOrder(models.Model):
    _inherit = "stock.picking"
