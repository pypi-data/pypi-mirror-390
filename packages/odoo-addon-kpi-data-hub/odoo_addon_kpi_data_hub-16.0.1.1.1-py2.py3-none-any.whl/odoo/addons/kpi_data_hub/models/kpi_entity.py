from odoo import fields, models


class KpiHubEntity(models.Model):
    _name = "kpi_hub.entity"
    _description = "KPI Hub Entity"

    name = fields.Char(required=True, copy=False)
    partner_id = fields.Many2one("res.partner", string="Partner")
    record_ids = fields.One2many("kpi_hub.record", "entity_id", string="Data Records")
    company_id = fields.Many2one(
        "res.company", string="Company", default=lambda self: self.env.company
    )
    active = fields.Boolean(default=True)

    _sql_constraints = [("name_uniq", "unique (name)", "Entity name must be unique.")]
