{
    "name": "BANCAT Software Management System",
    "author": "BANCAT",
    "license": "LGPL-3",
    "category": "Services",
    "summary": 'Manage patient and donor details, bed allocation, and hospital information',
    "description": """
            A module to manage patient and donor details, bed allocation, and hospital information.
        """,
    "depends": ['base', 'mail','documents'],
    "data": [
        'security/ir.model.access.csv',
        # 'views/assets.xml',
        'views/bsms_patient_view.xml',
        'views/cancer_type_view.xml',
        'views/bed_allocation_view.xml',
        'views/cancer_hospital_view.xml',
        'views/bsms_attendance_view.xml',
        'views/menuitems.xml',

        "data/patient_cancer_type.xml",
        "data/bed_allocation.xml",
        "data/cancer_hospital.xml"

    ],
    'demo': [
    ],
    # 'assets': {
    #     'web.assets_backend': [
    #         'custom_addons/bancat_management_system/static/src/js/list_editable_add_label.js',
    #     ],
    # },
    "installable": True,
    "auto_install": False,
    "application": True,
}
