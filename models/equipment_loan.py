import math

from odoo import models, fields, api
from odoo.exceptions import ValidationError, AccessError
from odoo.osv import expression

class EquipmentLoan(models.Model):
    _name = "equipment.loan"
    _description = "Equipment Loan"

    _inherit = [
        "mail.thread",
        "mail.activity.mixin",
    ]

    name = fields.Char(
        string="Loan Reference",
        required=True,
        copy=False,
        readonly=True,
        default="New",
    )

    item_id = fields.Many2one(
        "equipment.item",
        string="Equipment",
        required=True,
    )
    borrower_id = fields.Many2one(
        "res.users",
        string="Borrower",
        required=True,
        default=lambda self: self.env.user,
    )

    date_start = fields.Datetime(
        string="Start Date",
        required=True,
        default=fields.Datetime.now,
    )

    date_due = fields.Datetime(
        string="Due Date",
        required=True,
        tracking=True,
    )
    date_return = fields.Datetime(
        string="Return Date",
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("returned", "Returned"),
            ("cancelled", "Cancelled"),
        ],
        string="Status",
        default="draft",
        tracking=True,
        required=True,
    )
    days_late = fields.Integer(
        string="Days Late",
        compute="_compute_days_late",
        store=True,
    )

    penalty_amount = fields.Monetary(
        string="Penalty",
        compute="_compute_penalty_amount",
        store=True,
        currency_field="currency_id",
    )

    currency_id = fields.Many2one(
        "res.currency",
        related="item_id.currency_id",
        store=True,
        readonly=True,
    )
    is_overdue = fields.Boolean(
        string="Overdue",)


    notes = fields.Html(
        string="Notes",
    )

    @api.constrains("date_due", "date_start")
    def _check_date(self):
        for loan in self:

            if loan.date_due < loan.date_start:
                raise ValidationError("Due Date cannot be less than start date.")

    @api.ondelete(at_uninstall=False)
    def _unlink_except_draft_or_cancelled(self):
        for loan in self:
            if loan.state in ("confirmed", "returned"):
                raise ValidationError(
                    "Only Draft or Cancelled loans can be deleted."
                )

    @api.depends("days_late", "item_id.daily_rate", )
    def _compute_penalty_amount(self):
        for loan in self:
            loan.penalty_amount = (
                    loan.days_late * loan.item_id.daily_rate
            )

    @api.depends("date_due", "date_return")
    def _compute_days_late(self):
        for loan in self:
            loan.days_late = 0

            if loan.date_due and loan.date_return:
                delay = loan.date_return - loan.date_due

                if delay.total_seconds() > 0:
                    loan.days_late = math.ceil(
                        delay.total_seconds() / 86400
                    )


    @api.model_create_multi
    def create(self, vals_list):

        for vals in vals_list:

            if vals.get("name", "New") == "New":
                vals["name"] = self.env[
                    "ir.sequence"
                ].next_by_code(
                    "equipment.loan"
                )

        return super().create(vals_list)


    def action_confirm(self):
        if not self.env.user.has_group(
                "porcelia_equipment_loan.group_equipment_manager"
        ):
            raise AccessError(
                "Only Equipment Managers can confirm loans."
            )
        for loan in self:
            if loan.state != "draft":
                raise ValidationError(
                    "Only draft loans can be confirmed."
                )


            conflicting_loan = self.search([
                ("id", "!=", loan.id),
                ("item_id", "=", loan.item_id.id),
                ("state", "=", "confirmed"),
                ("date_return", "=", False),
                ("date_start", "<", loan.date_due),
                ("date_due", ">", loan.date_start),
            ], limit=1)

            if conflicting_loan:
                raise ValidationError(
                    f"This item is already booked in "
                    f"{conflicting_loan.name}."
                )


            loan.state = "confirmed"

    def action_return(self):
        for loan in self:
            if loan.state != "confirmed":
                raise ValidationError(
                    "Only confirmed loans can be returned."
                )

            if not loan.date_return:
                loan.date_return = fields.Datetime.now()

            loan.state = "returned"

    def action_open_return_wizard(self):
        if not self:
            raise ValidationError("No loans were selected.")

        invalid = self.filtered(lambda loan: loan.state != "confirmed")
        if invalid:
            raise ValidationError("Only confirmed loans can be returned")


        context = dict(self.env.context)
        context.update({
            "active_model": "equipment.loan",
            "active_ids": self.ids,
            "active_id": self.ids[0],
            "default_loan_ids": [(6, 0, self.ids)],
        })
        if len(self) == 1:
            context["default_condition_score"] = self.item_id.condition_score or 0

        return {
            "type": "ir.actions.act_window",
            "name": "Return Equipment",
            "res_model": "equipment.loan.return.wizard",
            "view_mode": "form",
            "view_id": self.env.ref(
                "porcelia_equipment_loan.equipment_loan_return_wizard_form"
            ).id,
            "target": "new",
            "context": context,
        }

    def action_cancel(self):
        for loan in self:
            if loan.state not in ("draft", "confirmed"):
                raise ValidationError(
                    "Only draft or confirmed loans can be cancelled."
                )

            loan.state = "cancelled"

    def action_draft(self):
        for loan in self:
            if loan.state not in ("cancelled", "returned"):
                raise ValidationError(
                    "Only cancelled or returned loans can be reset to draft."
                )

            loan.state = "draft"





    @api.model
    def _cron_mark_overdue_loans(self):
        loans = self.search([
            ("state", "=", "confirmed"),
            ("date_due", "<", fields.Datetime.now()),
            ("date_return", "=", False),
            ("is_overdue", "=", False),
        ])

        for loan in loans:
            loan.is_overdue = True

            loan.message_post(
                body=f"Loan {loan.name} is overdue."
            )

            loan.activity_schedule(
                "mail.mail_activity_data_todo",
                user_id=loan.borrower_id.id,
                summary="Overdue Equipment Loan",
                note=f"Loan {loan.name} is overdue. Please return the equipment.",
            )

    @api.model
    def get_dashboard_data(self, period):
        Loan = self.env["equipment.loan"]
        Item = self.env["equipment.item"]

        total_items = Item.search_count([
            ("active", "=", True)
        ])

        items_on_loan = Item.search_count([
            ("active", "=", True),
            ("state", "=", "on_loan")
        ])

        overdue_count = Loan.search_count([
            ("state", "=", "confirmed"),
            ("is_overdue", "=", True),
            ("date_return", "=", False)
        ])

        today = fields.Date.context_today(self)

        if period == "week":
            start_date = fields.Date.start_of(today, "week")

        elif period == "month":
            start_date = fields.Date.start_of(today, "month")

        else:
            start_date = False

        penalty_domain = [
            ("penalty_amount", ">", 0),
            ("date_return", "!=", False),
        ]

        if start_date:
            penalty_domain.append(
                ("date_return", ">=", start_date)
            )

        penalty_loans = Loan.search(penalty_domain)

        top_overdue = Loan.search(
            [
                ("state", "=", "confirmed"),
                ("is_overdue", "=", True),
                ("date_return", "=", False),
            ],
            order="date_due asc",
            limit=5,
        )

        return {
            "total_items": total_items,
            "items_on_loan": items_on_loan,
            "overdue_loans": overdue_count,
            "total_penalties": sum(
                penalty_loans.mapped("penalty_amount")
            ),
            "top_overdue": [
                {
                    "id": loan.id,
                    "reference": loan.name,
                    "item": loan.item_id.display_name,
                    "borrower": loan.borrower_id.display_name,
                    "days_late": max(
                        0,
                        (fields.Datetime.now() - loan.date_due).days
                    ),
                }
                for loan in top_overdue
            ],
        }
    
