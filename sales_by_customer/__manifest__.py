# -*- coding: utf-8 -*-
{
    'name': "Todoterreno Custom reports",

    'summary': """Reporte de ventas por cliente y reporte personalizado de inventario en pantalla y excel""",

    'description': """
        Reporte de ventas por cliente y reporte personalizado de inventario en pantalla y excel
    """,

    'author': "Exetic Soluciona",
    'website': "https://www.exeticsoluciona.com",

    'category': 'Custom',
    'version': '13.0.0.8',

    'depends': ['sale_management', "stock"],

    'data': [
        'security/ir.model.access.csv',
        'wizards/sales_customer_wizard_view.xml',
        'wizards/product_inventory_wizard_view.xml',
        'reports/sales_customer_template.xml',
        'reports/product_inventory_template.xml',
    ],
}
