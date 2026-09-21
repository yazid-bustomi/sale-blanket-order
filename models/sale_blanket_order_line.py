# -*- coding: utf-8 -*-
from odoo import fields, models, api


class SaleBlanketOrderLine(models.Model):
    """Add production/costing fields to a Blanket Order line: an internal
    ("secondary") price and finish/production info.
    """
    _inherit = 'sale.blanket.order.line'

    info_to_buyer = fields.Text(
        string="Info to Buyer",
        copy=False,
        help='Information to buyer',
    )
    info_to_production = fields.Text(
        string="Info to Production",
        help="Information provided to the production team."
    )
    type_product = fields.Selection(
        selection=[
            ('int', 'INT'),
            ('ext', 'EXT'),
            ('hdl', 'HDL'),
        ],
        string="Type",
        store=True,
        help="Type Proction",
        default='int'
    )

    # Points directly at res.partner rather than a dedicated "supplier
    # order" model: this is meant to record which subcontracted workshop
    # produces this line, and re-using res.partner lets it be any partner
    # already known to the system instead of duplicating contact data.
    supp_order = fields.Many2one(
        'res.partner',
        string="Supp",
        store=True,
    )

    # "Internal Price" (also used verbatim in the reports and the Request
    # DP wizard) is the customer-facing label for this secondary/internal
    # price basis; see `sec_price`, the underlying field name.
    sec_price = fields.Float(
        string="Internal Price",
        help="Secondary/internal price basis, used for margin tracking "
             "and as an optional Down Payment base (see Request DP)."
    )

    total_sec_price = fields.Float(
        string='Total Cust Price',
        compute='_compute_total_sec_price',
        store=True
    )

    @api.depends('sec_price', 'original_uom_qty')
    def _compute_total_sec_price(self):
        for record in self:
            record.total_sec_price = record.sec_price * record.original_uom_qty

    finish = fields.Char(string='Finish')

    finish_product = fields.Many2one('product.finish', string='Finish Product')

    due_date_item_update = fields.Date(string='Due Date Item Update')

    color_attribute_size = fields.Char(string='Color / Attribute / Size')

    analytic_names = fields.Char(compute='_compute_analytic_names', string='Analytic Names')

    def _compute_analytic_names(self):
        """Resolve the raw {account_id: percentage} analytic_distribution
        JSON into a human-readable, comma-separated list of account names
        for display on list views and reports."""
        for line in self:
            if line.analytic_distribution:
                ids = [int(i) for i in line.analytic_distribution.keys()]
                names = self.env['account.analytic.account'].browse(ids).mapped('name')
                line.analytic_names = ', '.join(names)
            else:
                line.analytic_names = ''
