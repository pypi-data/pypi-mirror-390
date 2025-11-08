import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class KpiHubTemplate(models.Model):
    _name = "kpi_hub.template"
    _description = "KPI Hub Data Template"

    name = fields.Char(required=True)
    item_template_ids = fields.One2many(
        "kpi_hub.item.template", "template_id", string="Data Items", copy=True
    )
    mis_report_template_id = fields.Many2one("mis.report", string="MIS Report Template")

    # Versioning system
    version = fields.Integer(
        string="Version",
        default=1,
        readonly=True,
        copy=False,  # No copiar al duplicar - nueva plantilla = nuevo historial
        help="Template version number. Increments when template is modified.",
    )
    version_date = fields.Datetime(
        string="Version Date",
        readonly=True,
        copy=False,  # No copiar al duplicar
        help="Date when this version was created",
    )
    version_changes = fields.Text(
        string="Version Changes",
        readonly=True,
        copy=False,  # No copiar al duplicar
        help="Description of changes made in this version",
    )
    previous_version_id = fields.Many2one(
        "kpi_hub.template",
        string="Previous Version",
        readonly=True,
        copy=False,  # No copiar al duplicar - nueva plantilla no tiene versión previa
        help="Reference to the previous version of this template",
    )

    # Related records tracking
    record_ids = fields.One2many(
        "kpi_hub.record", "template_id", string="Data Records", readonly=True
    )
    outdated_record_count = fields.Integer(
        string="Outdated Records",
        compute="_compute_outdated_record_count",
        store=False,  # Don't store to avoid computation issues during install
        help="Number of data records using outdated template versions",
    )

    @api.depends("record_ids.is_outdated")
    def _compute_outdated_record_count(self):
        """Compute count of records using outdated template versions."""
        for template in self:
            try:
                # Skip computation during installation to avoid issues
                if self.env.context.get("install_mode"):
                    template.outdated_record_count = 0
                else:
                    template.outdated_record_count = len(
                        template.record_ids.filtered("is_outdated")
                    )
            except Exception:
                template.outdated_record_count = 0

    def _increment_version(self, changes_description=None):
        """Increment template version and create history."""
        self.ensure_one()

        # Create a copy of current template as previous version
        # Only copy essential fields to avoid issues with computed fields
        previous_version_vals = {
            "name": f"{self.name} (v{self.version})",
            "version": self.version,
            "version_date": self.version_date,
            "active": False,  # Archive previous version
            "item_template_ids": [
                (6, 0, self.item_template_ids.ids)
            ],  # Copy item templates
        }

        try:
            previous_version = self.create(previous_version_vals)
        except Exception as e:
            _logger.warning(
                f"Could not create previous version for template {self.name}: {e}"
            )
            # Continue without creating history
            previous_version = self.env["kpi_hub.template"]

        # Update current template directly (avoid triggering write method again)
        super(KpiHubTemplate, self).write(
            {
                "version": self.version + 1,
                "version_date": fields.Datetime.now(),
                "version_changes": changes_description or _("Template updated"),
                "previous_version_id": previous_version.id
                if previous_version
                else False,
            }
        )

        _logger.info(f"Template {self.name} updated to version {self.version + 1}")
        return True

    def write(self, vals):
        """Override write to handle versioning when template changes."""
        # Skip versioning during module installation/update
        if self.env.context.get("install_mode") or self.env.context.get(
            "update_module"
        ):
            return super(KpiHubTemplate, self).write(vals)

        # Check if any significant fields are being changed
        significant_fields = ["name", "item_template_ids"]

        changing_significant_fields = any(field in vals for field in significant_fields)

        if changing_significant_fields:
            # Increment version for each template being modified
            for template in self:
                changes_desc = self._get_changes_description(vals)
                template._increment_version(changes_desc)

            # Remove version fields from vals to avoid infinite recursion
            vals_to_write = vals.copy()
            vals_to_write.pop("version", None)
            vals_to_write.pop("version_date", None)
            vals_to_write.pop("version_changes", None)
            vals_to_write.pop("previous_version_id", None)
        else:
            vals_to_write = vals

        return super(KpiHubTemplate, self).write(vals_to_write)

    def _get_changes_description(self, vals):
        """Generate description of changes made."""
        changes = []
        if "name" in vals:
            changes.append(_("Name changed"))
        if "item_template_ids" in vals:
            changes.append(_("KPI items modified"))

        return "; ".join(changes) if changes else _("Template modified")

    def action_view_outdated_records(self):
        """Action to view records using outdated template versions."""
        self.ensure_one()
        outdated_records = self.record_ids.filtered("is_outdated")

        return {
            "name": _("Outdated Records"),
            "type": "ir.actions.act_window",
            "res_model": "kpi_hub.record",
            "view_mode": "tree,form",
            "domain": [("id", "in", outdated_records.ids)],
            "context": {"default_template_id": self.id},
        }


class KpiHubItemTemplate(models.Model):
    _name = "kpi_hub.item.template"
    _description = "KPI Hub Data Item Template"
    _order = "sequence, id"

    sequence = fields.Integer(default=10)
    name = fields.Char(required=True, translate=True)
    code = fields.Char(
        required=True,
        help="Code used for formulas. Must be uppercase and have no spaces.",
    )
    template_id = fields.Many2one(
        "kpi_hub.template", string="Template", required=True, ondelete="cascade"
    )
    data_source_info = fields.Char(string="Data Source Information")
    calculation_type = fields.Selection(
        [("data", "Data Input"), ("formula", "Formula"), ("group", "Group Total")],
        default="data",
        required=True,
    )
    formula = fields.Char(
        string="Formula", help="Use item codes in uppercase. Example: ITEM1 + ITEM2"
    )

    # Campos para jerarquía y agrupación
    parent_id = fields.Many2one(
        "kpi_hub.item.template",
        string="Parent Item",
        help="Parent item for hierarchical grouping",
    )
    child_ids = fields.One2many(
        "kpi_hub.item.template", "parent_id", string="Child Items"
    )
    level = fields.Integer(string="Level", compute="_compute_level", store=True)
    is_group = fields.Boolean(
        string="Is Group", compute="_compute_is_group", store=True
    )

    # Campos para tipo de datos y validaciones
    data_type = fields.Selection(
        [
            ("integer", "Integer"),
            ("float", "Decimal"),
            ("percentage", "Percentage"),
            ("currency", "Currency"),
            ("boolean", "Yes/No"),
        ],
        string="Data Type",
        default="float",
    )

    min_value = fields.Float(string="Minimum Value")
    max_value = fields.Float(string="Maximum Value")
    decimal_places = fields.Integer(string="Decimal Places", default=2)
    is_required = fields.Boolean(string="Required", default=False)
    default_value = fields.Float(string="Default Value", default=0.0)

    # Campos para formateo
    prefix = fields.Char(string="Prefix", help="Text before value (e.g., $, €)")
    suffix = fields.Char(string="Suffix", help="Text after value (e.g., %, kg)")

    # Campo para auto-suma de hijos
    auto_sum_children = fields.Boolean(
        string="Auto Sum Children",
        default=False,
        help="Automatically sum all child items",
    )

    @api.depends("parent_id")
    def _compute_level(self):
        for record in self:
            level = 0
            parent = record.parent_id
            while parent:
                level += 1
                parent = parent.parent_id
            record.level = level

    @api.depends("child_ids", "calculation_type")
    def _compute_is_group(self):
        for record in self:
            record.is_group = (
                bool(record.child_ids) or record.calculation_type == "group"
            )

    @api.onchange("auto_sum_children")
    def _onchange_auto_sum_children(self):
        if self.auto_sum_children:
            self.calculation_type = "formula"
            # Generar fórmula automática basada en hijos
            if self.child_ids:
                child_codes = [child.code for child in self.child_ids if child.code]
                if child_codes:
                    self.formula = " + ".join(child_codes)

    @api.onchange("parent_id")
    def _onchange_parent_id(self):
        # Actualizar fórmula del padre si tiene auto_sum_children activado
        if self.parent_id and self.parent_id.auto_sum_children:
            child_codes = [
                child.code for child in self.parent_id.child_ids if child.code
            ]
            if child_codes:
                self.parent_id.formula = " + ".join(child_codes)

    @api.constrains("parent_id")
    def _check_parent_recursion(self):
        if not self._check_recursion():
            raise ValidationError(_("You cannot create recursive hierarchies."))

    @api.constrains("min_value", "max_value")
    def _check_min_max_values(self):
        for record in self:
            if (
                record.min_value
                and record.max_value
                and record.min_value > record.max_value
            ):
                raise ValidationError(
                    _("Minimum value cannot be greater than maximum value.")
                )

    @api.constrains("decimal_places")
    def _check_decimal_places(self):
        for record in self:
            if record.decimal_places < 0 or record.decimal_places > 6:
                raise ValidationError(_("Decimal places must be between 0 and 6."))

    def create_child_item(self, name, code, **kwargs):
        """Helper method to create child items"""
        vals = {
            "name": name,
            "code": code,
            "parent_id": self.id,
            "template_id": self.template_id.id,
            "sequence": self.sequence + 10,
            **kwargs,
        }
        return self.create(vals)

    _sql_constraints = [
        (
            "code_template_uniq",
            "unique (code, template_id)",
            "The code must be unique per template.",
        )
    ]


# Removed duplicated KpiHubItemValue model. The actual model and compute logic
# live in kpi_data_record.py to avoid conflicts and ensure consistent behavior.
