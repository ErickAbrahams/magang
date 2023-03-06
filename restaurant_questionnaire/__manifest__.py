# -*- coding: utf-8 -*-
{
    'name': "Restaurant Questionnaire",

    'summary': """
        Provide Restaurant questionnaire for halal / non-halal""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'product', 'stock', 'portal', 'website_sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'views/stock_picking.xml',
        'views/views.xml',
        'views/partner.xml',
        'views/templates.xml',
        'views/website_sale.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
