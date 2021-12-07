# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name" : "Second Unit of Measure",
    "author" : "Softhealer Technologies",
    "website": "https://exeticsoluciona.com",
    "support": "aramirez@exeticsoluciona.com",
    "category": "Extra Tools",
    "summary": "sales secondary uom app, purchase secondary unit of measure, request for quotation multiple uom odoo, account double uom, warehouse multiple unit Odoo",
    "description": """Second Unit of Measure
    """,
    "version":"13.0.4",
    "depends" : [
                    "sale_management",
                    "account",
                    "purchase",
                    "stock",
                ],
    "application" : True,
    "data" : [
            "security/secondary_unit_group.xml",
            "views/sh_product_template_custom.xml",
            "views/sh_product_custom.xml",
            "views/sh_sale_order_view.xml",
            "views/sh_purchase_order_view.xml",
            "views/sh_stock_picking_view.xml",
            "views/sh_stock_move_view.xml",
            "views/sh_account_invoice_view.xml",
            "views/sh_stock_scrap_view.xml",
            "report/sh_report_sale_order.xml",
            "report/sh_report_purchase_order.xml",
            "report/sh_report_account_invoice_view.xml",
            "report/sh_report_stock_picking_operation.xml",
            "report/sh_report_deliveryslip.xml",
            ],
    "auto_install":False,
    "installable" : True,
}
