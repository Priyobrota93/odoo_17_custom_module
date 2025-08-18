# -*- coding: utf-8 -*-
{
    'name': 'Custom Hello',
    'version': '1.0',
    'author': "CLAREx",
    'category': 'Tools',
    'summary': 'A simple Hello module',
    'description': 'Demo module that stores simple hello messages.',
    'license': 'LGPL-3',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/hello_message_views.xml',
    ],

    'demo': [
        'demo/demo1.xml',

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

