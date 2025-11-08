import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class KpiTemplateVersionUpdateWizard(models.TransientModel):
    """Wizard to update multiple KPI records to latest template version."""

    _name = "kpi_template_version_update_wizard"
    _description = "KPI Template Version Update Wizard"

    # Context-based fields
    template_id = fields.Many2one(
        "kpi_hub.template",
        string="Template",
        readonly=True,
        help="Template to update records for",
    )

    record_ids = fields.Many2many(
        "kpi_hub.record",
        string="Records to Update",
        readonly=True,
        help="KPI records that will be updated",
    )

    # Summary information
    total_records = fields.Integer(
        string="Total Records", compute="_compute_totals", readonly=True
    )

    outdated_records = fields.Integer(
        string="Outdated Records", compute="_compute_totals", readonly=True
    )

    # Operation options
    update_option = fields.Selection(
        [
            ("selected", "Update Selected Records"),
            ("all_outdated", "Update All Outdated Records for Template"),
            ("entity", "Update Records for Specific Entity"),
        ],
        string="Update Scope",
        default="selected",
        required=True,
    )

    entity_id = fields.Many2one(
        "kpi_hub.entity",
        string="Entity Filter",
        help="When updating by entity, only records for this entity will be updated",
        attrs="{'required': [('update_option', '=', 'entity')]}",
    )

    # Results
    updated_count = fields.Integer(string="Records Updated", readonly=True)
    skipped_count = fields.Integer(string="Records Skipped", readonly=True)
    error_count = fields.Integer(string="Errors", readonly=True)

    @api.model
    def default_get(self, fields_list):
        """Set default values based on context."""
        res = super().default_get(fields_list)

        # Get active records from context
        active_ids = self.env.context.get("active_ids", [])
        active_model = self.env.context.get("active_model")

        if active_model == "kpi_hub.record" and active_ids:
            records = self.env["kpi_hub.record"].browse(active_ids)
            res["record_ids"] = [(6, 0, active_ids)]

            # Set template from first record (assuming all have same template)
            if records:
                res["template_id"] = records[0].template_id.id

        elif active_model == "kpi_hub.template" and active_ids:
            template = self.env["kpi_hub.template"].browse(active_ids[0])
            res["template_id"] = template.id
            res["update_option"] = "all_outdated"

        return res

    @api.depends("record_ids", "template_id")
    def _compute_totals(self):
        """Compute summary statistics."""
        for wizard in self:
            if wizard.record_ids:
                wizard.total_records = len(wizard.record_ids)
                wizard.outdated_records = len(wizard.record_ids.filtered("is_outdated"))
            elif wizard.template_id:
                wizard.total_records = len(wizard.template_id.record_ids)
                wizard.outdated_records = wizard.template_id.outdated_record_count
            else:
                wizard.total_records = 0
                wizard.outdated_records = 0

    def _get_records_to_update(self):
        """Get the list of records to update based on selected option."""
        self.ensure_one()

        if self.update_option == "selected":
            return self.record_ids
        elif self.update_option == "all_outdated":
            return self.template_id.record_ids.filtered("is_outdated")
        elif self.update_option == "entity":
            if not self.entity_id:
                raise UserError(_("Please select an entity for entity-based updates."))
            return self.template_id.record_ids.filtered(
                lambda r: r.entity_id == self.entity_id and r.is_outdated
            )
        else:
            return self.env["kpi_hub.record"]

    def action_update_versions(self):
        """Execute the version update operation."""
        self.ensure_one()

        records_to_update = self._get_records_to_update()

        if not records_to_update:
            raise UserError(_("No records found to update."))

        updated = 0
        skipped = 0
        errors = 0

        for record in records_to_update:
            try:
                result = record.action_sync_with_template()
                if (
                    result.get("type") == "ir.actions.client"
                    and result.get("tag") == "display_notification"
                ):
                    if result["params"].get("type") == "success":
                        updated += 1
                    else:
                        errors += 1
                else:
                    # Assume success if no error notification
                    updated += 1
            except Exception as e:
                _logger.error(f"Error updating record {record.name}: {str(e)}")
                errors += 1

        # Update wizard results
        self.write(
            {
                "updated_count": updated,
                "skipped_count": skipped,
                "error_count": errors,
            }
        )

        # Return result message
        message = _("Version update completed.\n")
        message += _("Updated: %s\n") % updated
        if skipped > 0:
            message += _("Skipped: %s\n") % skipped
        if errors > 0:
            message += _("Errors: %s\n") % errors

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Version Update Complete"),
                "message": message,
                "type": "success" if errors == 0 else "warning",
                "sticky": True,
            },
        }

    def action_view_results(self):
        """View the results of the update operation."""
        self.ensure_one()

        # This would show a summary of what was updated
        # For now, just close the wizard
        return {"type": "ir.actions.act_window_close"}
