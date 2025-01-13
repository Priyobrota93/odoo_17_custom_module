{
    "name": "Access_Mobile_HRx",
    "author": "CLAREx",
    "license": "LGPL-3",
    "depends": ["hr", "hr_attendance","base",'hr_expense','hr_holidays'],
    "data": [
    
        "views/hr_mobile_access.xml",
        "views/hr_attendance_request_view.xml",
        "views/mobile_access_view.xml",
        "views/menuitem.xml",
        
        
        


        "security/ir.model.access.csv",
        # "data/scheduled_actions.xml",
        # # "data/hr_email_templates.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
}
