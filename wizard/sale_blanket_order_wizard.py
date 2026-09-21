# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import re

import pytz

from odoo import fields, models, api, exceptions


class SaleBlanketOrderWizard(models.TransientModel):
    """Extend the OCA "Create Sale Order" wizard with backdating: lets a
    Sales Order drawn from a Blanket Order be entered into Odoo today but
    dated as if it had been created earlier, and renumbered accordingly.
    """
    _inherit = 'sale.blanket.order.wizard'
    _description = 'Create BackDate '

    date_create_sale_order = fields.Date(
        string="Create SO",
        help="Tanggal pembuatan Sales Order",
        copy=False,
        required=True
    )

    @api.model
    def _get_next_sequence(self, year, month):
        """Compute the next 5-digit running number for an ``SO
        YY/MM/NNNNN`` name, scoped to year/month."""
        last_request = self.env["sale.order"].search([
            ("name", "like", f"SO {year}/{month}/%"),
        ], order="name desc", limit=1)

        if last_request:
            match = re.search(rf"SO {year}/{month}/(\d+)", last_request.name)
            if match:
                last_number = int(match.group(1))
                return f"{last_number + 1:05d}"
            else:
                raise exceptions.ValidationError(
                    f"Format nama SO tidak sesuai: {last_request.name}"
                )
        else:
            return "00001"

    def create_sale_order(self):
        """Create the Sales Order as usual, then rename/redate it using
        the user-provided backdate instead of "now".

        The new order's *time* still comes from the current moment (only
        the date is backdated), converted through Asia/Jakarta so the
        stored UTC timestamp reflects the same local wall-clock time the
        business actually works in.
        """
        res = super().create_sale_order()

        for record in self:
            if not record.date_create_sale_order:
                raise exceptions.ValidationError("Tanggal 'Create SO' harus diisi!")

            wizard_line = self.env["sale.blanket.order.wizard.line"].search([
                ("wizard_id", "=", record.id)
            ], limit=1)

            if not wizard_line or not wizard_line.order_id:
                raise exceptions.ValidationError("Blanket Order tidak ditemukan di Wizard!")

            blanket_order = wizard_line.order_id

            jakarta_tz = pytz.timezone("Asia/Jakarta")
            now_jakarta = datetime.now(jakarta_tz)

            local_datetime = datetime.combine(record.date_create_sale_order, now_jakarta.time())
            localized_datetime = jakarta_tz.localize(local_datetime)
            utc_datetime = localized_datetime.astimezone(pytz.utc)
            naive_utc_datetime = utc_datetime.replace(tzinfo=None)

            # WIB = Western Indonesia Time (UTC+7); needed again here (as
            # in sale_blanket_order.action_confirm) purely to compute the
            # year/month bucket for the sequence, independent of the
            # precise localized timestamp above.
            date_bo_wib = datetime.combine(record.date_create_sale_order, datetime.min.time()) + timedelta(hours=7)

            year = date_bo_wib.strftime("%y")
            month = date_bo_wib.strftime("%m")
            sequence = self._get_next_sequence(year, month)

            new_name = f"SO {year}/{month}/{sequence}"

            # The wizard just created a sale.order from this Blanket
            # Order; find it back via `origin` (Odoo stamps the source
            # document's name there) since create_sale_order() only
            # returns an action, not the new record.
            sale_order = self.env["sale.order"].search([
                ("origin", "=", blanket_order.name)
            ], order="id desc", limit=1)

            if sale_order:
                sale_order.write({
                    "name": new_name,
                    "date_order": naive_utc_datetime,
                    "validity_date": record.date_create_sale_order
                })
            else:
                raise exceptions.ValidationError(f"Gagal menemukan Sales Order dengan origin {blanket_order.name}")

        return res
