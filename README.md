# Sale Blanket Order - Backdating, Pricing & Pro Forma Reports

Odoo 18 addon that adds the numbering, backdating, secondary pricing and
export-grade Pro Forma / Master SO PDF reports a real export business
needs on top of the OCA/Acsone `sale_blanket_order` module.

> Extracted from a real Odoo export/manufacturing implementation.
> Company-specific data has been removed; the business logic and workflow
> are unchanged. One decorative photo in a confirmation dialog (of an
> identifiable person, unrelated to this module's own code) was removed
> during that clean-up — see **Sanitization notes** below.

## Why this module

The OCA `sale_blanket_order` module models a long-running "master order"
that individual Sales Orders are drawn from over time - exactly how an
export customer typically commits to a large order that gets produced
and shipped in batches. What it doesn't provide out of the box is: a
human-readable, sequential document numbering scheme; the ability to
enter paperwork after the fact but have it dated as if entered on time;
a second, internal price basis for margin tracking; a down-payment
workflow; and the specific paperwork (Pro Forma Invoice, Master SO/MTO)
an export order actually needs, with QR codes, dimensions in both cm and
inches, and the customer's own product codes.

## Features

- **Sequential numbering**: `BO YYYY/MM/NNNNN` for Blanket Orders and
  `SO YYYY/MM/NNNNN` for Sales Orders drawn from them, assigned on
  confirmation.
- **Backdating**: both the Blanket Order and the "Create Sale Order"
  wizard accept a "Create BO"/"Create SO" date used for numbering and
  the stored order date, so paperwork entered late still reflects the
  real commercial date.
- **Secondary ("OM") price** per line for internal margin tracking,
  rolled up into its own order total alongside the customer-facing total.
- **Request DP wizard**: compute a down payment as a percentage (of
  either price basis) or a fixed amount; the result is shown on the Pro
  Forma Invoice.
- **Production fields** per line: Finish, Info to Buyer/Production,
  Color/Attribute/Size, a subcontractor reference, and the customer's own
  product code (via `om_sale_external_id`).
- **Six PDF report variants**:
  - Pro Forma Invoice - single-page or auto-paginated, with or without a
    product photo per line.
  - Master SO / MTO report - "final" and "Draft" (with an extra
    production-notes block), each with QR codes for the customer PO
    reference and the internal order number.

## Requirements

- Odoo **18.0**
- [`sale_blanket_order`](https://github.com/OCA/sale-workflow) - a
  **third-party OCA/Acsone module**; install it from the OCA
  `sale-workflow` repository. This addon only extends it, it does not
  replace it.
- Standard `account` and `stock` apps.
- [`om_sale_external_id`](https://github.com/yazid-bustomi/om_sale_external_id) -
  a sibling module by the same author, published separately in this
  portfolio.
- Python package [`qrcode`](https://pypi.org/project/qrcode/) (for the
  QR codes on the Master SO / MTO reports):
  ```bash
  pip install qrcode
  ```

## Installation

1. Install `sale_blanket_order` from OCA `sale-workflow`, then
   `om_sale_external_id` from this portfolio.
2. `pip install qrcode`.
3. Copy this folder into your Odoo `addons` path:
   ```bash
   cp -r om_sale_blanket_order_it /path/to/odoo/addons/
   ```
4. Restart the server and update the apps list
   (`Settings > Apps > Update Apps List`, with developer mode enabled).
5. Search for **"Sale Blanket Order - Backdating, Pricing & Pro Forma
   Reports"** and click **Install**.

## Usage

1. Create a **Blanket Order** (**Sales > Orders > Blanket Orders**), fill
   in the lines including **OM Price**, **Finish**, **Info to
   Buyer/Production**, etc.
2. Set **Create BO** to the real commercial date if you are entering the
   order after the fact, then click **Confirm** - the order is renamed
   to `BO YY/MM/NNNNN` based on that date.
3. Click **Request DP** in the header to open the down-payment wizard;
   pick a percentage (of Price or OM Price) or a fixed amount and
   **Confirm** - the result appears in the **Request DP** field and on
   the Pro Forma Invoice.
4. Use **Create Sale Order** as usual; the wizard now also asks for a
   **Create SO** date, used the same way for the `SO YY/MM/NNNNN` name.
5. From the Blanket Order's **Print** menu, choose the report that fits:
   **Pro Forma Invoice** (RH or General, with or without photo) for the
   customer-facing invoice, or **Master SO Report** (final or Draft) for
   the internal/production paperwork.

## Sanitization notes

- All company identification on the printed reports (name, address, bank
  details, logo) is pulled dynamically from `res.company` /
  `res.partner.bank` - no company data is hardcoded anywhere in this
  module.
- One `<img>` in a confirmation dialog, in the sibling
  `om_purchase_order_it` module, referenced a photo of an identifiable
  person and was removed there (not part of this module) - see that
  module's README.

## Project structure

```
om_sale_blanket_order_it/
├── models/
│   ├── product_finish.py          # product.finish master list
│   ├── sale_blanket_order.py      # numbering, backdating, QR codes
│   └── sale_blanket_order_line.py # secondary price, production fields
├── wizard/
│   ├── sale_blanket_order_wizard.py     # backdated "Create Sale Order"
│   └── request_dp_blanket_order.py      # Request DP wizard
├── reports/
│   ├── pro_forma_reports.xml                        # paper format + actions
│   ├── report_pro_forma_invoice_*_with_photo.xml     # Pro Forma, with photo
│   ├── report_pro_forma_invoice_*_no_photo.xml       # Pro Forma, no photo
│   ├── report_mpo.xml                                # Master SO report +
│   │                                                  # shared body template
│   └── report_mto_draft.xml                          # Master SO (Draft)
├── views/                          # form/tree/line view extensions
└── security/                       # access rights
```

## License

Licensed under [LGPL-3](LICENSE).

## Author

**Akhmad Yazid Bustomi**
GitHub: [github.com/yazid-bustomi](https://github.com/yazid-bustomi)
