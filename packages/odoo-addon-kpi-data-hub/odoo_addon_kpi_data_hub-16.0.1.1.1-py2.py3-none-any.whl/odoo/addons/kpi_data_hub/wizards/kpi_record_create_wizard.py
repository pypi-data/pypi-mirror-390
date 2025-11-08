from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class KpiRecordCreateWizard(models.TransientModel):
    """Wizard to create new KPI records with template selection."""

    _name = "kpi_record_create_wizard"
    _description = "Create KPI Record Wizard"

    # Record basic information
    entity_id = fields.Many2one(
        "kpi_hub.entity",
        string="Entity",
        required=True,
        help="The entity for which to create the KPI record",
    )

    template_id = fields.Many2one(
        "kpi_hub.template",
        string="Template",
        required=True,
        help="The KPI template to use for this record",
    )

    # Date information
    date_range_id = fields.Many2one(
        "date.range", string="Date Range", help="Optional date range for the record"
    )

    date_from = fields.Date(string="Start Date", help="Start date for the KPI period")

    date_to = fields.Date(string="End Date", help="End date for the KPI period")

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
        help="Company for this KPI record",
    )

    @api.onchange("date_range_id")
    def _onchange_date_range_id(self):
        """Set dates from date range."""
        if self.date_range_id:
            self.date_from = self.date_range_id.date_start
            self.date_to = self.date_range_id.date_end

    @api.onchange("template_id")
    def _onchange_template_id(self):
        """Validate template selection."""
        if self.template_id:
            # Check if a record already exists for this combination
            existing = self.env["kpi_hub.record"].search(
                [
                    ("entity_id", "=", self.entity_id.id if self.entity_id else False),
                    ("template_id", "=", self.template_id.id),
                    ("date_from", "=", self.date_from),
                    ("date_to", "=", self.date_to),
                    ("company_id", "=", self.company_id.id),
                ],
                limit=1,
            )

            if existing:
                raise ValidationError(
                    _(
                        "A KPI record already exists for this Entity, Template, and Period combination."
                    )
                )

    def action_create_record(self):
        """Create the KPI record with the selected template."""
        self.ensure_one()

        # Validate required fields
        if not self.entity_id or not self.template_id:
            raise ValidationError(_("Entity and Template are required."))

        # Create the record
        vals = {
            "entity_id": self.entity_id.id,
            "template_id": self.template_id.id,
            "company_id": self.company_id.id,
        }

        # Add dates if provided
        if self.date_from:
            vals["date_from"] = self.date_from
        if self.date_to:
            vals["date_to"] = self.date_to
        if self.date_range_id:
            vals["date_range_id"] = self.date_range_id.id

        # Create the record
        record = self.env["kpi_hub.record"].create(vals)

        # Return action to open the created record
        return {
            "type": "ir.actions.act_window",
            "res_model": "kpi_hub.record",
            "res_id": record.id,
            "view_mode": "form",
            "target": "current",
        }
