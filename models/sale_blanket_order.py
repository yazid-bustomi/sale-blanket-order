# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from io import BytesIO
import base64

import qrcode

from odoo import fields, models, api, exceptions


class SaleBlanketOrder(models.Model):
    """Add backdating, sequential numbering and the production/pricing
    fields a real export Blanket Order workflow needs.
    """
    _inherit = 'sale.blanket.order'
    _description = 'Backdate Sale Blanket Order'

    date_create_blanket_order = fields.Date(
        string="Create BO",
        help="Date Create Blanket Order",
        copy=False,
        default=fields.Date.today
    )
    currency_id = fields.Many2one('res.currency', string="Currency")
    req_dp_amount = fields.Monetary(string="Request DP", currency_field='currency_id')
    ket_request_dp = fields.Char('Ket Request Dp')
    production_time = fields.Integer(string="Production Time")
    partner_bank_id = fields.Many2one(
        comodel_name='res.partner.bank',
        string='Recipient Bank',
        domain="[('partner_id.ref_company_ids', 'parent_of', company_id)]"
    )
    due_date_update_order = fields.Date(
        string="Due Date Update",
        store=True,
        copy=False,
        tracking=True
    )
    client_order_ref = fields.Char(string="PO")
    po_cust = fields.Char(string="PO Cust")
    confirmation_date_order = fields.Date(string="Confirmation Date Order")
    due_date_order = fields.Date(string="Due Date")

    billing_partner_id = fields.Many2one('res.partner', string='Billing Partner', compute='_compute_billing_partner')
    payment_info = fields.Text(string="Payment Info")

    cutting_order_lot = fields.Text(
        string="Cutting Order / Lot"
    )

    order_remarks_for_production = fields.Text(
        string="Order Remarks for Production",
        help="Remarks for production team"
    )

    order_admin_update = fields.Text(
        string="Order Admin Update",
        help="Admin update notes"
    )

    total_order_qty = fields.Float(
        string="Total Order",
        compute="_compute_total_qty_order"
    )

    amount_total_sec_price = fields.Float(
        string="Total OM Price",
        compute='_compute_amount_total_sec_price',
        store=True
    )

    @api.depends('partner_id')
    def _compute_billing_partner(self):
        """Bill the parent company when the order's contact is a child
        contact (e.g. a specific buyer/department), otherwise bill the
        contact itself."""
        for rec in self:
            rec.billing_partner_id = rec.partner_id.parent_id if rec.partner_id.parent_id else rec.partner_id

    @api.depends('line_ids.original_uom_qty')
    def _compute_total_qty_order(self):
        for order in self:
            order.total_order_qty = sum(order.line_ids.mapped('original_uom_qty'))

    @api.depends('line_ids.total_sec_price')
    def _compute_amount_total_sec_price(self):
        for order in self:
            order.amount_total_sec_price = sum(line.total_sec_price for line in order.line_ids)

    @api.model
    def _get_next_sequence(self, year, month):
        """Compute the next 5-digit running number for a ``BO
        YY/MM/NNNNN`` name, scoped to the given year/month so the counter
        resets every month instead of growing forever."""
        last_request = self.search([
            ("name", "like", f"BO {year}/{month}/%"),
        ], order="name desc", limit=1)

        if last_request:
            try:
                last_number_str = last_request.name.split('/')[-1]
                last_number = int(last_number_str)
            except (ValueError, IndexError):
                last_number = 0
            next_number = last_number + 1
        else:
            next_number = 1

        return f"{next_number:05d}"

    def action_confirm(self):
        """Rename the order to ``BO YYYY/MM/NNNNN`` on confirmation, using
        the (possibly backdated) "Create BO" date rather than today's date
        - so a Blanket Order entered late still gets a number consistent
        with when it was actually agreed, not when it was typed into Odoo.
        """
        res = super().action_confirm()

        for record in self:
            if not record.date_create_blanket_order:
                raise exceptions.ValidationError("Tanggal 'Create BO' harus diisi!")

            # WIB = Western Indonesia Time (UTC+7); the sequence's
            # year/month must follow the business's local calendar, not
            # whatever timezone the server happens to run in.
            date_bo_wib = datetime.combine(record.date_create_blanket_order, datetime.min.time()) + timedelta(hours=7)

            year = date_bo_wib.strftime("%y")
            month = date_bo_wib.strftime("%m")
            sequence = self._get_next_sequence(year, month)

            new_name = f"BO {year}/{month}/{sequence}"

            if self.search([("name", "=", new_name)]):
                raise exceptions.ValidationError(f"Nama {new_name} sudah digunakan, mohon coba lagi.")

            record.name = new_name
        return res

    def action_wizard_dp_blanket_order(self):
        """Open the Request DP wizard for this order (see
        wizard/request_dp_blanket_order.py)."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Request DP',
            'res_model': 'wizard.request.dp.blanket.order',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_blanket_order_id': self.id,
            }
        }

    def get_qr_code(self, data):
        """Render `data` (e.g. the customer PO reference or this order's
        own name) as a base64 PNG, for the QR codes printed on the
        Master SO / MTO reports."""
        if data:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(data)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            return base64.b64encode(buffer.getvalue()).decode()
        return ''
