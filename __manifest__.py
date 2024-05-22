{
    'name': "scan_serial_transfer",
    'author': "saad",
    'category': 'tools',
    'version': "16.0.0.1.0",
    'depends': ['base', 'stock', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/import_exal.xml',
        'views/server_action.xml',
        'views/add_boolean_button.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application':False,
}
