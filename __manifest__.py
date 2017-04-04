# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Maple Transform',
    'category': '',
    'version': '1.0',
    'author': "Benoit Vézina & Pierre Dalpé pour Portall",
    'website': "portall.ca",
    'summary': 'Adding rules and action to transform raw maple syrup',
    'description':
        """
This module allow to transform raw maple product from either classification or mixing/transformation
        """,
    'depends': [
        'maple',
    ],
    'data': [
        'data/ir_sequence_data.xml',
#        'views/stock_quant_views.xml',
        'wizard/maple_transform_wizard.xml',
        'views/maple_classification.xml',
    ],
    'qweb': [
#        "static/src/xml/*.xml",
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}

