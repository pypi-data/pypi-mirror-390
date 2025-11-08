import logging
import re

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class KpiHubRecord(models.Model):
    _name = "kpi_hub.record"
    _description = "KPI Hub Data Record"

    name = fields.Char(compute="_compute_name", store=True, readonly=True)
    entity_id = fields.Many2one(
        "kpi_hub.entity",
        string="Entity",
        required=True,
        ondelete="cascade",
        track_visibility="onchange",
    )
    template_id = fields.Many2one(
        "kpi_hub.template",
        string="Template",
        track_visibility="onchange",
    )
    date_range_id = fields.Many2one(
        "date.range", string="Date Range", track_visibility="onchange"
    )
    date_from = fields.Date(string="Start Period", track_visibility="onchange")
    date_to = fields.Date(string="End Period", track_visibility="onchange")
    value_ids = fields.One2many(
        "kpi_hub.item.value",
        "record_id",
        string="Data Values",
        copy=True,
        default=lambda self: self._default_value_ids(),
    )
    company_id = fields.Many2one(
        "res.company", string="Company", default=lambda self: self.env.company
    )
    active = fields.Boolean(default=True)

    code = fields.Char(
        string="Code",
        required=True,
        readonly=True,
        default=lambda self: self.env["ir.sequence"].next_by_code("kpi_hub.record"),
        copy=False,
    )

    # Template versioning tracking
    template_version = fields.Integer(
        string="Template Version",
        readonly=True,
        help="Version of the template when this record was created/updated",
    )
    template_version_date = fields.Datetime(
        string="Template Version Date",
        readonly=True,
        help="Date when the template version was captured",
    )
    is_outdated = fields.Boolean(
        string="Template Outdated",
        compute="_compute_is_outdated",
        store=False,  # Don't store initially to avoid install issues
        help="True if the record uses an outdated template version",
    )
    outdated_message = fields.Text(
        string="Outdated Message",
        compute="_compute_outdated_message",
        help="Explanation of why the record is outdated",
    )

    # Related fields for template information (for easier access in views)
    template_version_current = fields.Integer(
        related="template_id.version",
        string="Current Template Version",
        readonly=True,
        help="Current version of the associated template",
    )
    template_version_date_current = fields.Datetime(
        related="template_id.version_date",
        string="Current Template Version Date",
        readonly=True,
        help="Date when the current template version was created",
    )
    template_version_changes_current = fields.Text(
        related="template_id.version_changes",
        string="Current Template Changes",
        readonly=True,
        help="Description of changes in the current template version",
    )

    _sql_constraints = [
        (
            "entity_template_period_uniq",
            "unique(entity_id, template_id, date_from, date_to, company_id)",
            "A data record for this entity, template and period already exists.",
        ),
    ]

    @api.model
    def create(self, vals):
        # Validate that template is provided when creating record
        if not vals.get("template_id"):
            raise ValidationError(
                _("Template is required to create a KPI Data Record.")
            )

        # Capture template version when creating record
        if "template_id" in vals:
            template = self.env["kpi_hub.template"].browse(vals["template_id"])
            vals["template_version"] = template.version
            vals["template_version_date"] = (
                template.version_date or fields.Datetime.now()
            )

        # Clean up any value_ids that don't have item_template_id (for single record)
        if "value_ids" in vals:
            cleaned_value_ids = []
            for value_cmd in vals["value_ids"]:
                if len(value_cmd) == 3 and value_cmd[0] == 0:  # (0, 0, {values})
                    value_data = value_cmd[2]
                    if (
                        "item_template_id" in value_data
                        and value_data["item_template_id"]
                    ):
                        cleaned_value_ids.append(value_cmd)
                else:
                    cleaned_value_ids.append(value_cmd)
            vals["value_ids"] = cleaned_value_ids

        record = super(KpiHubRecord, self).create(vals)

        # Only create item values if template is set and no values exist
        if record.template_id and not record.value_ids:
            record._create_item_values()
        # Calculate formulas after creating item values
        if record.value_ids:
            record.action_calculate_formulas()
        return record

    def write(self, vals):
        # Skip template synchronization if we're just updating version fields
        if self.env.context.get("skip_template_sync"):
            return super(KpiHubRecord, self).write(vals)

        # Validate template changes
        if "template_id" in vals:
            new_template_id = vals["template_id"]
            for record in self:
                if record.template_id and record.template_id.id != new_template_id:
                    # Template is being changed - this should go through the wizard
                    if not self.env.context.get("allow_template_change"):
                        raise UserError(
                            _(
                                "Use the 'Change Template' button to change the template."
                            )
                        )
                elif not record.template_id and not new_template_id:
                    raise ValidationError(_("Template is required."))

        result = super(KpiHubRecord, self).write(vals)

        # Handle template changes
        if "template_id" in vals:
            for record in self:
                # Update template version info
                if record.template_id:
                    record.with_context(skip_template_sync=True).write(
                        {
                            "template_version": record.template_id.version,
                            "template_version_date": record.template_id.version_date
                            or fields.Datetime.now(),
                        }
                    )

                # Synchronize item values with new template using special context
                # This will add new items and remove obsolete ones (including calculated items)
                record.with_context(
                    syncing_template=True
                )._sync_item_values_with_template()

                # Calculate formulas after synchronization
                record.action_calculate_formulas()

        return result

    def _create_item_values(self):
        """Create item values for all template items if they don't exist"""
        self.ensure_one()
        if not self.template_id:
            return

        # Get existing item template IDs to avoid duplicates
        existing_item_ids = self.value_ids.mapped("item_template_id.id")
        vals_list = []

        for item_template in self.template_id.item_template_ids:
            if item_template.id not in existing_item_ids:
                # Set default value based on data type for required fields
                default_value = 0.0
                if item_template.is_required:
                    if item_template.data_type == "currency":
                        default_value = 0.0
                    elif item_template.data_type == "integer":
                        default_value = 0
                    elif item_template.data_type == "percentage":
                        default_value = 0.0
                    # For other types, use 0.0

                vals_list.append(
                    {
                        "record_id": self.id,
                        "item_template_id": item_template.id,
                        "value": default_value,
                    }
                )

        if vals_list:
            self.env["kpi_hub.item.value"].create(vals_list)

    @api.depends("entity_id.name", "template_id.name", "date_to")
    def _compute_name(self):
        for record in self:
            year = record.date_to.year if record.date_to else ""
            name_parts = [record.template_id.name, record.entity_id.name, str(year)]
            record.name = " - ".join(filter(None, name_parts))

    @api.onchange("date_range_id")
    def _onchange_date_range_id(self):
        if self.date_range_id:
            self.date_from = self.date_range_id.date_start
            self.date_to = self.date_range_id.date_end

    @api.depends("template_id.version", "template_version")
    def _compute_is_outdated(self):
        """Check if the record uses an outdated template version."""
        for record in self:
            try:
                # Skip computation during installation to avoid issues
                if self.env.context.get("install_mode"):
                    record.is_outdated = False
                elif record.template_id and record.template_version is not None:
                    record.is_outdated = (
                        record.template_version < record.template_id.version
                    )
                else:
                    record.is_outdated = False
            except Exception:
                record.is_outdated = False

    @api.depends(
        "is_outdated",
        "template_id.version",
        "template_version",
        "template_id.version_date",
        "template_version_date",
    )
    def _compute_outdated_message(self):
        """Generate message explaining why the record is outdated."""
        for record in self:
            try:
                # Skip computation during installation to avoid issues
                if self.env.context.get("install_mode"):
                    record.outdated_message = ""
                elif not record.is_outdated or not record.template_id:
                    record.outdated_message = ""
                else:
                    version_diff = record.template_id.version - record.template_version
                    template_date = record.template_id.version_date

                    message = _(
                        "This record uses template version %s but the current template version is %s (%s versions behind)."
                    ) % (
                        record.template_version,
                        record.template_id.version,
                        version_diff,
                    )

                    if template_date:
                        message += _(
                            " Latest template update: %s"
                        ) % template_date.strftime("%Y-%m-%d %H:%M")

                    record.outdated_message = message
            except (AttributeError, TypeError, Exception):
                record.outdated_message = _("Template version information unavailable.")

    def action_open_change_template_wizard(self):
        return {
            "type": "ir.actions.act_window",
            "name": _("Change Template"),
            "res_model": "kpi_data_hub.warning",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_record_id": self.id,
            },
        }

    def _get_kpi_value_from_other_record(self, kpi_code, code):
        """
        Get a KPI value from another record using its unique code.
        Provided in formula contexts as GET_KPI. Ensures the target record
        recalculates formulas/groups using the current calculation stack to
        avoid circular dependencies.
        """
        self.ensure_one()
        item_value_model = self.env["kpi_hub.item.value"]

        # Find the target item value in the other record
        domain = [
            ("record_id.code", "=", code),
            ("item_template_id.code", "=", kpi_code),
            ("record_id.company_id", "=", self.company_id.id),
        ]
        target_item_value = item_value_model.search(domain, limit=1)

        if not target_item_value:
            return 0.0

        # For data fields, just return the stored value
        if target_item_value.calculation_type == "data":
            return target_item_value.value

        # For formula/group, recalculate the target record with propagated stack
        current_stack = self.env.context.get("calculation_stack", set())
        target_record = target_item_value.record_id
        target_record.with_context(
            calculation_stack=current_stack
        ).action_calculate_formulas()
        return target_item_value.value

    def _get_formula_context(self):
        """Get context with all current values for formula calculation"""
        self.ensure_one()
        context = {}
        for item in self.value_ids:
            if item.item_template_id and item.item_template_id.code:
                context[item.item_template_id.code.upper()] = item.value

        # Add the GET_KPI function to the context, wrapped in a lambda to pass the stack
        context["GET_KPI"] = (
            lambda kpi_code, code: self._get_kpi_value_from_other_record(kpi_code, code)
        )
        return context

    def action_calculate_formulas(self):
        """Calculate formulas and group totals with safe eval and cycle checks"""
        for record in self:
            # Use existing calculation stack from context, if any
            stack = record.env.context.get("calculation_stack", set())
            # Ensure we do not recursively trigger recalculation while writing values
            record_ctx = record.with_context(
                calculation_stack=stack, skip_formula_recalc=True
            )

            if not record_ctx.value_ids:
                continue

            # Formula items
            formula_items = record_ctx.value_ids.filtered(
                lambda i: i.calculation_type == "formula" and i.formula
            ).sorted("sequence")

            # Evaluate formulas
            for item in formula_items:
                try:
                    item_key = (record_ctx.id, item.item_template_id.id)
                    if item_key in stack:
                        raise ValidationError(
                            _(
                                "Circular dependency detected for item '%s' in record '%s'."
                            )
                            % (item.name, record_ctx.name)
                        )

                    # Local stack for nested GET_KPI calls
                    local_stack = set(stack)
                    local_stack.add(item_key)

                    # Build evaluation context
                    base_ctx = {}
                    for iv in record_ctx.value_ids:
                        if iv.item_template_id and iv.item_template_id.code:
                            base_ctx[iv.item_template_id.code.upper()] = iv.value

                    allowed = {
                        "__builtins__": {},
                        "abs": abs,
                        "round": round,
                        "min": min,
                        "max": max,
                        "sum": sum,
                    }
                    allowed.update(base_ctx)

                    # GET_KPI closure propagating local stack
                    def _GET_KPI(kpi_code, code):
                        return record_ctx.with_context(
                            calculation_stack=local_stack
                        )._get_kpi_value_from_other_record(kpi_code, code)

                    allowed["GET_KPI"] = _GET_KPI

                    # Normalize and preprocess expression (support unquoted GET_KPI args)
                    expr = (item.formula or "").upper().strip()
                    expr = re.sub(
                        r"GET_KPI\(\s*([A-Z0-9_]+)\s*,\s*([A-Z0-9_-]+)\s*\)",
                        r"GET_KPI('\1','\2')",
                        expr,
                    )

                    result = eval(expr, allowed, {})
                    # Write with context to avoid recursive recalculation
                    item.with_context(skip_formula_recalc=True).write(
                        {"value": float(result or 0.0)}
                    )
                except Exception as e:
                    _logger.warning(
                        "Error evaluating formula for item '%s' in record '%s': %s",
                        item.name,
                        record_ctx.name,
                        e,
                    )
                    item.with_context(skip_formula_recalc=True).write({"value": 0.0})

            # Group items: sum direct children
            group_items = record_ctx.value_ids.filtered(
                lambda i: i.calculation_type == "group"
            )
            for g in group_items:
                try:
                    children = record_ctx.value_ids.filtered(
                        lambda v: v.item_template_id.parent_id.id
                        == g.item_template_id.id
                    )
                    g.with_context(skip_formula_recalc=True).write(
                        {"value": sum(c.value for c in children)}
                    )
                except Exception as e:
                    _logger.warning(
                        "Error computing group for item '%s' in record '%s': %s",
                        g.name,
                        record_ctx.name,
                        e,
                    )
                    g.with_context(skip_formula_recalc=True).write({"value": 0.0})

    def _default_value_ids(self):
        """Create default value_ids based on context template_id"""
        template_id = self.env.context.get("default_template_id")
        if template_id:
            template = self.env["kpi_hub.template"].browse(template_id)
            if template.exists():
                vals_list = []
                for item_template in template.item_template_ids:
                    vals_list.append(
                        (
                            0,
                            0,
                            {
                                "item_template_id": item_template.id,
                                "value": 0.0,
                            },
                        )
                    )
                return vals_list
        return []

    def action_sync_with_template(self):
        """Synchronize this record with the current template version."""
        self.ensure_one()

        if not self.template_id:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Error"),
                    "message": _("No template associated with this record."),
                    "type": "danger",
                },
            }

        # Update template version info
        self.write(
            {
                "template_version": self.template_id.version,
                "template_version_date": self.template_id.version_date
                or fields.Datetime.now(),
            }
        )

        # Sync item values with current template
        self._sync_item_values_with_template()

        # Recalculate formulas
        self.action_calculate_formulas()

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Success"),
                "message": _("Record synchronized with template version %s.")
                % self.template_id.version,
                "type": "success",
            },
        }

    def _sync_item_values_with_template(self):
        """Synchronize item values with current template structure."""
        self.ensure_one()

        # Get current template items
        current_item_ids = set(self.template_id.item_template_ids.ids)

        # Get existing item values
        existing_item_ids = set(self.value_ids.mapped("item_template_id.id"))

        # Items to add (in template but not in record)
        items_to_add = current_item_ids - existing_item_ids

        # Items to remove (in record but not in template)
        items_to_remove = existing_item_ids - current_item_ids

        # Add missing items
        if items_to_add:
            vals_list = []
            for item_id in items_to_add:
                vals_list.append(
                    {
                        "record_id": self.id,
                        "item_template_id": item_id,
                        "value": 0.0,
                    }
                )
            if vals_list:
                self.env["kpi_hub.item.value"].create(vals_list)

        # Remove obsolete items
        if items_to_remove:
            obsolete_values = self.value_ids.filtered(
                lambda v: v.item_template_id.id in items_to_remove
            )
            if obsolete_values:
                # Use special context to allow deletion of calculated items during sync
                obsolete_values.with_context(syncing_template=True).unlink()

        _logger.info(
            "Synced record %s: added %s items, removed %s items",
            self.name,
            len(items_to_add),
            len(items_to_remove),
        )

    def action_view_template_history(self):
        """View the history of template versions."""
        self.ensure_one()

        return {
            "name": _("Template History"),
            "type": "ir.actions.act_window",
            "res_model": "kpi_hub.template",
            "view_mode": "tree,form",
            "domain": [
                "|",
                ("id", "=", self.template_id.id),
                ("previous_version_id", "=", self.template_id.id),
            ],
            "context": {
                "default_active": False,  # Show archived versions
            },
        }


class KpiHubItemValue(models.Model):
    _name = "kpi_hub.item.value"
    _description = "KPI Hub Data Item Value"
    _order = "sequence, id"

    record_id = fields.Many2one(
        "kpi_hub.record", string="Data Record", required=True, ondelete="cascade"
    )
    item_template_id = fields.Many2one(
        "kpi_hub.item.template", string="Data Item", required=True, ondelete="cascade"
    )
    value = fields.Float(string="Value", default=0.0)

    # Related fields for easy access in views
    name = fields.Char(related="item_template_id.name", readonly=True)
    code = fields.Char(related="item_template_id.code", readonly=True)
    calculation_type = fields.Selection(
        related="item_template_id.calculation_type", readonly=True
    )
    formula = fields.Char(related="item_template_id.formula", readonly=True)
    sequence = fields.Integer(
        related="item_template_id.sequence", readonly=True, store=True
    )

    # Related fields for hierarchy
    parent_id = fields.Many2one(related="item_template_id.parent_id", readonly=True)
    level = fields.Integer(related="item_template_id.level", readonly=True)
    is_group = fields.Boolean(related="item_template_id.is_group", readonly=True)
    auto_sum_children = fields.Boolean(
        related="item_template_id.auto_sum_children", readonly=True
    )

    # Related fields for data type validation and formatting
    data_type = fields.Selection(related="item_template_id.data_type", readonly=True)
    min_value = fields.Float(related="item_template_id.min_value", readonly=True)
    max_value = fields.Float(related="item_template_id.max_value", readonly=True)
    decimal_places = fields.Integer(
        related="item_template_id.decimal_places", readonly=True
    )
    is_required = fields.Boolean(related="item_template_id.is_required", readonly=True)
    prefix = fields.Char(related="item_template_id.prefix", readonly=True)
    suffix = fields.Char(related="item_template_id.suffix", readonly=True)

    # Computed field for formatted display
    formatted_value = fields.Char(
        string="Formatted Value", compute="_compute_formatted_value"
    )
    display_name_with_level = fields.Char(
        string="Display Name", compute="_compute_display_name_with_level"
    )

    @api.depends("value", "data_type", "decimal_places", "prefix", "suffix")
    def _compute_formatted_value(self):
        for record in self:
            if record.data_type == "integer":
                formatted = str(int(record.value))
            elif record.data_type == "percentage":
                formatted = f"{record.value:.{record.decimal_places}f}%"
            elif record.data_type == "currency":
                formatted = f"{record.value:,.{record.decimal_places}f}"
            elif record.data_type == "boolean":
                formatted = _("Yes") if record.value else _("No")
            else:  # float
                formatted = f"{record.value:.{record.decimal_places}f}"

            # Add prefix and suffix
            if record.prefix:
                formatted = f"{record.prefix}{formatted}"
            if record.suffix:
                formatted = f"{formatted}{record.suffix}"

            record.formatted_value = formatted

    @api.depends("name", "level")
    def _compute_display_name_with_level(self):
        for record in self:
            indent = "    " * record.level  # 4 spaces per level
            record.display_name_with_level = f"{indent}{record.name}"

    def unlink(self):
        """Override unlink to prevent deletion of calculated/group items only"""
        # Skip validation during:
        # - Demo data loading or installation
        # - Template synchronization (when updating to new template version)
        if (
            self.env.context.get("install_mode")
            or self.env.context.get("defer_parent_store_computation")
            or self.env.context.get("syncing_template")
        ):
            return super().unlink()

        for record in self:
            # Only prevent deletion of formula or group items (automatically calculated)
            if record.calculation_type in ["formula", "group"]:
                raise ValidationError(
                    _(
                        'Cannot delete item "%s" because it is a calculated/group item. '
                        "These items are automatically managed based on the template structure."
                    )
                    % record.name
                )

        return super().unlink()

    @api.constrains("value")
    def _check_value_constraints(self):
        # Skip validation during demo data loading
        if self.env.context.get("install_mode") or self.env.context.get(
            "defer_parent_store_computation"
        ):
            return

        for record in self:
            # Skip validation for formula items (they are calculated)
            if record.calculation_type in ["formula", "group"]:
                continue

            # Check if required field has value
            if record.is_required and not record.value:
                raise ValidationError(
                    _('Field "%s" is required and cannot be empty.') % record.name
                )

            # Check min/max values
            if record.min_value and record.value < record.min_value:
                raise ValidationError(
                    _('Value for "%s" cannot be less than %s.')
                    % (record.name, record.min_value)
                )

            if record.max_value and record.value > record.max_value:
                raise ValidationError(
                    _('Value for "%s" cannot be greater than %s.')
                    % (record.name, record.max_value)
                )

            # Check data type constraints
            if record.data_type == "integer" and record.value != int(record.value):
                raise ValidationError(
                    _('Field "%s" must be an integer value.') % record.name
                )

            if record.data_type == "percentage" and (
                record.value < 0 or record.value > 100
            ):
                raise ValidationError(
                    _('Percentage value for "%s" must be between 0 and 100.')
                    % record.name
                )

            if record.data_type == "boolean" and record.value not in [0, 1]:
                raise ValidationError(
                    _('Boolean field "%s" must be 0 (No) or 1 (Yes).') % record.name
                )

    def write(self, vals):
        """Override write to trigger formula recalculation when values change"""
        result = super(KpiHubItemValue, self).write(vals)

        # Only recalculate if value changed and we're not in skip mode
        if "value" in vals and not self.env.context.get("skip_formula_recalc"):
            # Get unique records that need recalculation
            records = self.mapped("record_id")
            for record in records:
                _logger.debug(
                    "Triggering formula recalculation for record '%s' due to value change",
                    record.name,
                )
                record.action_calculate_formulas()

        return result

    # Removed compute method to avoid recursion; calculation now lives in action_calculate_formulas
