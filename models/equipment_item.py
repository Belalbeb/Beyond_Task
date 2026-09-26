
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class EquipmentItem(models.Model):
    _name = "equipment.item"
    _description = "Equipment Item"

    name = fields.Char(required=True)

    code = fields.Char(
        required=True,
        copy=False,
        readonly=True,
        default="New"
    )
    category_id = fields.Many2one('equipment.category', required=True,String="Equipment Category")
    image_1920 = fields.Image()
    active = fields.Boolean(default=True)
    daily_rate = fields.Monetary(
        currency_field="currency_id"
    )
    currency_id = fields.Many2one(
        "res.currency",
        required=True,
        default=lambda self: self.env.company.currency_id
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
    condition_score = fields.Integer()
    state = fields.Selection(
        [
            ("available", "Available"),
            ("on_loan", "On Loan"),
            ("maintenance", "Maintenance"),
            ("scrapped", "Scrapped"),
        ],
        compute="_compute_state",
        store=True,
        default="available",
    )
    loan_ids = fields.One2many(
        "equipment.loan",
        "item_id",
        string="Loans"
    )
    loan_count = fields.Integer(compute="_compute_loan_count")

    total_days_on_loan = fields.Integer(compute="_compute_total_days_on_loan")

    _sql_constraints = [
        (
            "unique_code_per_company",
            "unique(code, company_id)",
            "Equipment code must be unique per company.",
        ),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:

            if vals.get("code", "New") == "New":
                code = self.env["ir.sequence"].next_by_code("equipment.item")

                vals["code"] = code

        return super().create(vals_list)

    @api.constrains("condition_score")
    def _check_condition_score(self):
        for record in self:
            if not 0 <= record.condition_score <= 100:
                raise ValidationError(
                    "Condition score must be between 0 and 100."
                )

    @api.depends('loan_ids')
    def _compute_loan_count(self):
        for record in self:
            record.loan_count = len(record.loan_ids)

    @api.depends("loan_ids.state", "loan_ids.date_return")
    def _compute_state(self):
        for record in self:
            active_loan = record.loan_ids.filtered(
                lambda loan: loan.state == "confirmed"
                             and not loan.date_return
            )
            record.state = "on_loan" if active_loan else "available"




    @api.depends("loan_ids.date_start","loan_ids.date_return","loan_ids.state",)
    def _compute_total_days_on_loan(self):
        if not self.ids:
            return

        self.env.cr.execute("""
            SELECT
                item_id,
                SUM(
                    EXTRACT(
                        EPOCH FROM (
                            COALESCE(date_return, NOW()) - date_start
                        )
                    ) / 86400
                )::INTEGER
            FROM equipment_loan
            WHERE item_id IN %s
              AND state IN ('confirmed', 'returned')
              AND date_start IS NOT NULL
            GROUP BY item_id
        """, [tuple(self.ids)])

        days_by_item = dict(self.env.cr.fetchall())

        for record in self:
            record.total_days_on_loan = days_by_item.get(record.id, 0)




    def action_view_loans(self):
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": "Equipment Loans",
            "res_model": "equipment.loan",
            "view_mode": "tree,form",
            "domain": [
                ("item_id", "=", self.id)
            ],
            "context": {
                "default_item_id": self.id,
            },
        }



