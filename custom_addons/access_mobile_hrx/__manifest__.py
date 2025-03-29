{
    "name": "Access_Mobile_HRx",
    "author": "CLAREx",
    "license": "LGPL-3",
    "depends": ["hr", "hr_attendance","base",'hr_expense','hr_holidays', 'mail'],
    "data": [
    
        "views/hr_mobile_access.xml",
        "views/hr_attendance_request_view.xml",
        "views/mobile_access_view.xml",
        "views/menuitem.xml",
        # "views/hr_email_templates.xml",

        
        
        


        "security/ir.model.access.csv",
        "data/hr_mobile_access_email_template.xml",
        # "data/hr_email_templates.xml",
        # "data/scheduled_actions.xml",

    ],
    "assets": {
            "web.assets_backend": [
                "/access_mobile_hrx/static/src/css/custom_styles.css"
            ],
        },
    "installable": True,
    "auto_install": False,
    "application": True,
}
