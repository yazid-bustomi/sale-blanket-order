# -*- coding: utf-8 -*-
from odoo import fields, models, api


class ProductFinish(models.Model):
    """A furniture/product "finish" (e.g. a paint colour or lacquer type).

    Kept as a small master-data model, rather than a free-text field on
    the order line, so the same finish can be referenced consistently
    across orders and printed on production/customer paperwork with both
    its name and its short code.
    """
    _name = 'product.finish'
    _description = 'Product Finish'
    _rec_name = 'display_name'

    name = fields.Char(string='Finish Name', required=True)
    code = fields.Char(string='Finish Code', required=True)
    display_name = fields.Char(compute='_compute_display_name', store=True)

    @api.depends('name', 'code')
    def _compute_display_name(self):
        for record in self:
            if record.name and record.code:
                record.display_name = f"{record.name} [{record.code}]"
            else:
                record.display_name = record.name or record.code or ''
