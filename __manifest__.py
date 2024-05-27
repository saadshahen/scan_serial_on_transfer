{
    'name': "scan_serial_transfer",
    'author': "saad",
    'category': 'tools',
    'version': "16.0.0.1.1",
    'depends': ['base', 'stock', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/import_exal.xml',
        'views/server_action.xml',
        'views/add_boolean_button.xml'
    ],
    # 'assets': {
    #     'web.assets_backend': [
    #         'server/odoo/custom_addons1/scan_serial_transfer/static/src/js/beep.js',
    #     ],
    # },
    'installable': True,
    'auto_install': False,
    'application':False,
}
