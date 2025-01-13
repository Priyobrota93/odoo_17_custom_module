{
    "name": "Real Estate Test",
    "author": "CLAREx",
    "description": """Real Estate module to show available properties""",
    "category": "Sales",
    "license": "LGPL-3",
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        'views/property_view.xml',
        'views/property_type_view.xml',
        'views/property_tag_view.xml',
        'views/property_offer_view.xml',
        "views/menu_items.xml",

        "data/property_type.xml",
        # "data/estate.property.type.csv",

    ],
    "demo": [
        "demo/property_tags.xml"

    ],
    "installable": True,
    "auto_install": False,
    "application": True,
}
