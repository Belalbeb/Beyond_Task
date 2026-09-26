/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class OverdueLoanSystray extends Component {
    static template = "porcelia_equipment_loan.OverdueLoanSystray";

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");

        this.state = useState({
            count: 0,
        });

        onWillStart(() => this.loadCount());
    }

    async loadCount() {
        this.state.count = await this.orm.searchCount(
            "equipment.loan",
            [
                ["borrower_id", "=", this.env.services.user.userId],
                ["state", "=", "confirmed"],
                ["is_overdue", "=", true],
                ["date_return", "=", false],
            ]
        );
    }

    openLoans() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "My Overdue Loans",
            res_model: "equipment.loan",
            views: [[false, "list"], [false, "form"]],
            domain: [
                ["borrower_id", "=", this.env.services.user.userId],
                ["state", "=", "confirmed"],
                ["is_overdue", "=", true],
                ["date_return", "=", false],
            ],
            target: "current",
        });
    }
}

registry.category("systray").add(
    "equipment_overdue_loans",
    {
        Component: OverdueLoanSystray,
        sequence: 10,
    }
);