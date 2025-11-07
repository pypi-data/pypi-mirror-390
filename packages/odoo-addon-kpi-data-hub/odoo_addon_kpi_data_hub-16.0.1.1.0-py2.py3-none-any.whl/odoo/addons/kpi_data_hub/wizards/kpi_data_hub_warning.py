from odoo import fields, models


class KpiDataHubWarning(models.TransientModel):
    _name = "kpi_data_hub.warning"
    _description = "KPI Data Hub Warning"

    template_id = fields.Many2one(
        "kpi_hub.template",
        string="New Template",
        required=True,
    )
    record_id = fields.Many2one("kpi_hub.record")

    def confirm(self):
        record = self.record_id

        # Clear existing values
        record.value_ids.unlink()

        # Write the new template_id
        record.write({"template_id": self.template_id.id})

        return {"type": "ir.actions.act_window_close"}
