{
    "name": "Directory Management System",
    "author": "CLAREx",
    "license": "LGPL-3",
    "depends": [ "base","contacts","sms"],
    "data": [
        "security/ir.model.access.csv",
        "views/scheduler.xml",
        "views/birthday_sms_scheduler.xml",
        "views/birthday_action_create.xml",
        # "views/eid_ul_adaha_scheduler.xml",
        "views/res_partner_inherit_views.xml",
        "data/birthday_wish_email_template.xml",
        # "data/birthday_wish_sms_template.xml",
        "data/role_base_birthday_wish_template.xml",
        "data/buddha_purnima_email_template.xml",
        "data/christmas_email_template.xml",
        "data/eid_ul_adha_email_template.xml",
        "data/eid_ul_fitr_email_template.xml",
        "data/independence_day_email_template.xml",
        "data/language_day_email_template.xml",
        "data/new_year_email_template.xml",
        "data/victory_day_email_template.xml",
        "data/durga_puja_email_template.xml",
        "data/pohela_boishakh_email_template.xml",
        # "data/dms_relation_type.xml",



    ],
    "assets": {
    },
    "installable": True,
    "auto_install": False,
    "application": True,
}