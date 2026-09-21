# -*- coding: utf-8 -*-
# Part of sale_blanket_order. See LICENSE file for full copyright and licensing details.
{
    'name': 'Sale Blanket Order - Backdating, Pricing & Pro Forma Reports',
    'version': '18.0.1.0.0',
    'category': 'Sales',
    'summary': 'Add sequential naming, backdating, a secondary price/down-payment '
               'workflow, and a family of Pro Forma / MTO PDF reports to Blanket Orders.',
    'description': """
Sale Blanket Order - Backdating, Pricing & Pro Forma Reports
==============================================================
The OCA/Acsone ``sale_blanket_order`` module models a long-running master
order (a "Blanket Order") from which individual Sales Orders are drawn
over time - a common pattern in export/manufacturing where a customer
commits to a large order that is produced and shipped in batches.

This module adds the extra workflow a real export business needs around
that master order:

* **Sequential, human-readable numbering** (``BO YY/MM/NNNNN``) applied
  automatically on confirmation, and the ability to **backdate** both the
  Blanket Order and the Sales Orders drawn from it - useful when the
  paperwork is entered into Odoo after the fact but must still reflect
  the real commercial dates.
* A **secondary price** per line (independent of the customer-facing
  unit price) for internal margin tracking, alongside **Finish**,
  **Info to Buyer/Production**, and other production-facing fields.
* A **Request DP (down payment)** wizard that computes a down payment
  either as a percentage of the order total or as a fixed amount, based
  on either price basis.
* A family of **Pro Forma Invoice** and **Master SO (MTO)** PDF reports
  - with/without product photos, single-page or automatically paginated
  - built for the paperwork an export order actually needs (QR codes,
  bank details, and per-line dimensions in cm *and* inches).

Key features
------------
* Automatic ``BO YYYY/MM/NNNNN`` and ``SO YYYY/MM/NNNNN`` numbering on
  confirmation, unique per year/month.
* Backdating support on both the Blanket Order and the "Create Sale
  Order" wizard.
* Secondary ("internal") price per line, rolled up into an order total
  distinct from the customer-facing total.
* Request DP wizard (percentage or fixed amount, price-basis aware).
* Six PDF report variants: Pro Forma Invoice (single-page / paginated,
  with/without photo) and Master SO / MTO (final and draft).
* QR-code generation for the customer PO reference and the internal
  order number on the MTO reports.

Note on terminology: a handful of fields/messages keep their original
Indonesian business vocabulary (``catatan``, ``ket_request_dp``,
"Sisa" = remaining quantity) because that is the vocabulary used by the
sales/production teams this module was built for.
""",
    'author': 'Akhmad Yazid Bustomi',
    'website': 'https://github.com/yazid-bustomi',
    'maintainer': 'Akhmad Yazid Bustomi',
    'license': 'LGPL-3',
    'depends': ['sale_blanket_order', 'account', 'stock'],
    'external_dependencies': {
        'python': ['qrcode'],
    },
    'data': [
        'security/ir.model.access.csv',
        'reports/pro_forma_reports.xml',
        'reports/report_pro_forma_invoice_template_with_photo.xml',
        'reports/report_pro_forma_invoice_general_with_photo.xml',
        'reports/report_pro_forma_invoice_template_no_photo.xml',
        'reports/report_pro_forma_invoice_general_no_photo.xml',
        'reports/report_mpo.xml',
        'reports/report_mto_draft.xml',
        'views/product_finish_views.xml',
        'views/sale_blanket_order_line_views.xml',
        'views/sale_blanket_order_views.xml',
        'views/sale_blanket_order_tree.xml',
        'wizard/sale_blanket_order_wizard_views.xml',
        'wizard/request_dp_blanket_order_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
