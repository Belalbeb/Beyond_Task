{
    "name": "Equipment Loan",
    "version": "1.0",
    "author": "bebo",
    "depends": ['base','mail'],
    "data": [
        "security/equipment_groups.xml",
        "security/ir.model.access.csv",
        "security/equipment_security.xml",
        "views/equipment_loan_view.xml",
        "views/equipment_item_view.xml",
        "views/equipment_category_view.xml",
        "views/res_users_views.xml",
        "views/equipment_dashboard_action.xml",
        "views/equipment_menus.xml",
        "views/equipment_cron.xml",
        "views/equipment_loan_return_wizard_view.xml",
        "reports/equipment_loan_report.xml",
        "data/equipment_sequence.xml",
        "demo/equipment_demo.xml",


    ],
   "assets": {
    "web.assets_backend": [
        "porcelia_equipment_loan/static/src/components/condition_gauge/condition_gauge.js",
        "porcelia_equipment_loan/static/src/components/condition_gauge/condition_gauge.xml",
        "porcelia_equipment_loan/static/src/components/condition_gauge/condition_gauge.css",
        "porcelia_equipment_loan/static/src/components/dashboard/dashboard.js",
        "porcelia_equipment_loan/static/src/components/dashboard/dashboard.xml",
        "porcelia_equipment_loan/static/src/components/dashboard/dashboard.css",
        "porcelia_equipment_loan/static/src/components/systray/systray_overdue.js",
        "porcelia_equipment_loan/static/src/components/systray/systray_overdue.xml",
        "porcelia_equipment_loan/static/src/components/systray/systray_overdue.css",
    ],
},

}