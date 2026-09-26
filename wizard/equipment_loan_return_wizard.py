from odoo import models, fields, api
from odoo.exceptions import ValidationError


class EquipmentLoanReturnWizard(models.TransientModel):
    _name = "equipment.loan.return.wizard"
    _description = "Equipment Loan Return Wizard"

    loan_ids = fields.Many2many(
        "equipment.loan",
        string="Loans",
        required=True,
    )
    date_return = fields.Datetime(
        string="Return Date",
        default=fields.Datetime.now,
        required=True,
    )
    condition_score = fields.Integer(
        string="Condition Score",
        required=True,
    )
    note = fields.Text(
        string="Note",
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_ids = self.env.context.get("active_ids") or []
        if self.env.context.get("active_model") == "equipment.loan" and active_ids:
            if "loan_ids" in fields_list and not res.get("loan_ids"):
                res["loan_ids"] = [(6, 0, active_ids)]
        return res

    @api.constrains("condition_score")
    def _check_condition_score(self):
        for wizard in self:
            if not 0 <= wizard.condition_score <= 100:
                raise ValidationError(
                    "Condition score must be between 0 and 100."
                )

    def action_confirm(self):
        self.ensure_one()
        loans = self.loan_ids
        if not loans:
            loans = self.env["equipment.loan"].browse(
                self.env.context.get("active_ids", [])
            )

        if not loans:
            raise ValidationError("No loans were selected.")

        for loan in loans:
            if loan.state != "confirmed":
                raise ValidationError(
                    f"Loan {loan.name} cannot be returned."
                )

            loan.date_return = self.date_return
            loan.item_id.condition_score = self.condition_score
            loan.action_return()
            loan.message_post(
                body=(
                    f"Equipment returned. "
                    f"Condition score: {self.condition_score}. "
                    f"{self.note or ''}"
                )
            )

        return {
            "type": "ir.actions.act_window_close",
        }
