from odoo import models, fields


class ResUsers(models.Model):
    _inherit = "res.users"

    equipment_loan_ids = fields.One2many(
        "equipment.loan",
        "borrower_id",
        string="Equipment Loans",
    )