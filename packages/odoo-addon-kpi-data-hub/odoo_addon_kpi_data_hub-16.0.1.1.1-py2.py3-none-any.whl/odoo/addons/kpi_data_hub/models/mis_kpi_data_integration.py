from odoo import fields, models


class KpiHubMisReport(models.Model):
    """Link between a KPI Hub template and a MIS report."""

    _name = "kpi_hub.mis.report"
    _description = "KPI Hub MIS Report Integration"

    name = fields.Char(required=True)

    kpi_hub_template_id = fields.Many2one(
        "kpi_hub.template",
        string="KPI Hub Template",
        required=True,
        ondelete="cascade",
    )

    mis_report_id = fields.Many2one(
        "mis.report",
        string="MIS Report",
        required=False,
        ondelete="cascade",
        help="MIS Report to link with (optional for demonstration purposes)",
    )

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
        required=True,
    )

    active = fields.Boolean(default=True)

    auto_map_items = fields.Boolean(
        string="Auto-map KPI Items",
        default=True,
        help="Automatically create mappings for all KPI items in the template",
    )

    item_mapping_ids = fields.One2many(
        "kpi_hub.mis.item.mapping",
        "report_id",
        string="Item Mappings",
    )


class KpiHubMisItemMapping(models.Model):
    """Mapping between KPI Hub items and MIS report KPIs."""

    _name = "kpi_hub.mis.item.mapping"
    _description = "KPI Hub MIS Item Mapping"

    report_id = fields.Many2one(
        "kpi_hub.mis.report",
        string="Report",
        required=True,
        ondelete="cascade",
    )

    kpi_hub_item_id = fields.Many2one(
        "kpi_hub.item.template",
        string="KPI Hub Item",
        required=True,
        ondelete="cascade",
    )

    mis_kpi_id = fields.Many2one(
        "mis.report.kpi",
        string="MIS KPI",
        required=True,
        ondelete="cascade",
    )


class KpiHubAepSource(models.Model):
    """AEP Source for KPI Hub data."""

    _name = "kpi_hub.aep.source"
    _description = "AEP Source for KPI Hub Data"

    name = fields.Char(required=True)

    template_id = fields.Many2one(
        "kpi_hub.template",
        string="KPI Hub Template",
        required=True,
        ondelete="cascade",
    )

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
        required=True,
    )

    active = fields.Boolean(default=True)
