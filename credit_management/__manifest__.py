# -*- coding: utf-8 -*-
# Copyright 2020 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).

{
    'name': 'Credit Management',
    'summary': """
        Credit management options with Partner Credit Hold/Credit Limit""",
    'author': "Sodexis",
    'website': 'https://www.sodexis.com/',
    'version': '14.0.1.0.1',
    'installable': True,
    'license': 'OPL-1',
    'depends': [
        'base',
        'account',
        'sale_management',
        'stock',
        'payment',
        'sod_sale_payment_method',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'wizard/partner_credit_limit_view_warning.xml',
        'views/res_partner_view.xml',
        'views/sale_view.xml',
        'views/res_config_settings_views.xml',
        'views/account_journal_view.xml',
        'views/stock_picking_views.xml',
        'views/account_payment_term_view.xml',
    ],
    'price': 49.00,
    'currency': 'USD',
}
