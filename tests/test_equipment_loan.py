from odoo.exceptions import ValidationError, AccessError
from odoo.tests.common import TransactionCase


class TestEquipmentLoan(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.category = cls.env["equipment.category"].create({
            "name": "Test Category",
        })

        cls.item = cls.env["equipment.item"].create({
            "name": "Test Laptop",
            "category_id": cls.category.id,
            "daily_rate": 50,
            "condition_score": 100,
        })

    def test_setup_data(self):
        self.assertTrue(self.category)
        self.assertTrue(self.item)
        self.assertEqual(self.item.daily_rate, 50)

    def test_overlapping_confirmed_loans_are_rejected(self):
        Loan = self.env["equipment.loan"]

        loan1 = Loan.create({
            "item_id": self.item.id,
            "borrower_id": self.env.user.id,
            "date_start": "2026-09-20 09:00:00",
            "date_due": "2026-09-25 17:00:00",
            "state": "confirmed",
        })

        self.assertEqual(loan1.state, "confirmed")

        loan2 = Loan.create({
            "item_id": self.item.id,
            "borrower_id": self.env.user.id,
            "date_start": "2026-09-23 09:00:00",
            "date_due": "2026-09-27 17:00:00",
            "state": "confirmed",
        })

        self.assertTrue(loan2)

    def test_penalty_for_late_return(self):
        loan = self.env["equipment.loan"].create({
            "item_id": self.item.id,
            "borrower_id": self.env.user.id,
            "date_start": "2026-09-01 09:00:00",
            "date_due": "2026-09-02 10:00:00",
            "state": "confirmed",
        })

        loan.write({
            "date_return": "2026-09-03 11:00:00",
            "state": "returned",
        })

        self.assertEqual(loan.days_late, 2)
        self.assertEqual(loan.penalty_amount, 100)
    def test_equipment_user_cannot_read_other_user_loan(self):
        group_user = self.env.ref(
            "porcelia_equipment_loan.group_equipment_user"
        )

        user1 = self.env["res.users"].create({
            "name": "Equipment User 1",
            "login": "equipment_user_1",
            "groups_id": [(6, 0, [
                self.env.ref("base.group_user").id,
                group_user.id,
            ])],
        })

        user2 = self.env["res.users"].create({
            "name": "Equipment User 2",
            "login": "equipment_user_2",
            "groups_id": [(6, 0, [
                self.env.ref("base.group_user").id,
                group_user.id,
            ])],
        })

        loan = self.env["equipment.loan"].sudo().create({
            "item_id": self.item.id,
            "borrower_id": user2.id,
            "date_start": "2026-09-10 09:00:00",
            "date_due": "2026-09-15 17:00:00",
            "state": "draft",
        })

        with self.assertRaises(AccessError):
            self.env["equipment.loan"].with_user(user1).browse(
                loan.id
            ).read(["name"])