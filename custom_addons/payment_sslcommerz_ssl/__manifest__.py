{
    'name': "Payment Provider: SSLCommerz",
    'version': '1.0',
    'category': 'Accounting/Payment Providers',
    'sequence': 350,
    'summary': "A Payment provider covering Bangladesh.",
    'description': "SSLCOMMERZ is the largest payment gateway aggregator in Bangladesh and a pioneer in the FinTech industry since 2010.",
    'author': 'SSLCommerz',
    'maintainer': 'SSLCommerz',
    'support': 'integration@sslcommerz.com',
    'depends': ['payment'],
    'images': ['static/description/images/banner_1.png'],
    'data': [
        'views/payment_sslcommerz_templates.xml',
        'views/payment_provider_views.xml',

        'data/payment_methods_data.xml',
        'data/payment_provider_data.xml',
    ],

    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'license': 'LGPL-3',
}
