from odoo import models, fields, api

class EquipmentCategory(models.Model):
    _name = "equipment.category"
    _description = "Equipment Category"

    _parent_name = "parent_id"
    _parent_store = True

    name = fields.Char(
        required=True,
        translate=True
    )

    parent_id = fields.Many2one(
        "equipment.category",
        string="Parent Category"
    )

    child_ids = fields.One2many(
        "equipment.category",
        "parent_id",
        string="Child Categories"
    )

    parent_path = fields.Char(index=True)

    item_count = fields.Integer(
        compute="_compute_item_count"
    )

    @api.depends()
    def _compute_item_count(self):
        category_ids = [category.id for category in self if category.id]
        mapped = {}
        if category_ids:
            counts = self.env["equipment.item"]._read_group(
                [("category_id", "in", category_ids)],
                ["category_id"],
                ["__count"],
            )
            mapped = {category.id: count for category, count in counts}
        for category in self:
            category.item_count = mapped.get(category.id, 0)