import logging
import re

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class KpiHubAepSource(models.Model):
    """KPI Hub data source for MIS Builder AEP.

    This model provides a custom data source for the Accounting Expression Processor
    that allows MIS reports to directly reference KPI Hub data using expressions
    like 'kpi[KPI_CODE]' or 'kpi[KPI_CODE][date_range]'.
    """

    _name = "kpi_hub.aep.source"
    _description = "KPI Hub AEP Data Source"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)

    # Configuration for the data source
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
    )

    # Expression pattern for this source
    expression_pattern = fields.Char(
        string="Expression Pattern",
        default="kpi",
        help="Pattern to use in MIS expressions (e.g., 'kpi' for kpi[CODE])",
    )

    # Default date range if none specified
    default_date_range_id = fields.Many2one(
        "date.range",
        string="Default Date Range",
        help="Default date range to use when none is specified in the expression",
    )

    # Mapping configuration
    auto_map_items = fields.Boolean(
        string="Auto-map KPI Items",
        default=True,
        help="Automatically create mappings for all KPI items in the template",
    )

    @api.model
    def _register_with_mis_builder(self):
        """Register this AEP source with MIS Builder."""
        # This method will be called when MIS Builder initializes
        # to register KPI Hub expressions
        pass

    def get_kpi_value(self, kpi_code, date_from=None, date_to=None, company_id=None):
        """Get KPI value from KPI Hub for a specific period and company.

        Args:
            kpi_code (str): The KPI code to retrieve
            date_from (date): Start date (optional)
            date_to (date): End date (optional)
            company_id (int): Company ID (optional)

        Returns:
            float: The KPI value or 0.0 if not found
        """
        _logger.info(
            "KPI Hub AEP Source: get_kpi_value called with code=%s, date_from=%s, date_to=%s, company_id=%s",
            kpi_code,
            date_from,
            date_to,
            company_id,
        )

        # Use company from source if not specified
        if not company_id:
            company_id = self.company_id.id

        _logger.info("KPI Hub AEP Source: Using company_id=%s", company_id)

        # Find the KPI Hub template that contains this KPI
        item_template = self.env["kpi_hub.item.template"].search(
            [
                ("code", "=", kpi_code),
                ("template_id", "=", self.template_id.id),
            ],
            limit=1,
        )

        if not item_template:
            _logger.warning(
                "KPI Hub item with code '%s' not found in template '%s'",
                kpi_code,
                self.template_id.name,
            )
            return 0.0

        _logger.info(
            "KPI Hub AEP Source: Found item template: %s (type: %s)",
            item_template.name,
            item_template.calculation_type,
        )

        # Build domain for finding records
        domain = [
            ("template_id", "=", self.template_id.id),
            ("company_id", "=", company_id),
        ]

        # Add date filters if provided
        if date_from and date_to:
            domain.extend(
                [
                    ("date_from", "<=", date_to),
                    ("date_to", ">=", date_from),
                ]
            )
        elif self.default_date_range_id:
            # Use default date range if no dates specified
            domain.extend(
                [
                    ("date_from", "<=", self.default_date_range_id.date_end),
                    ("date_to", ">=", self.default_date_range_id.date_start),
                ]
            )

        _logger.info("KPI Hub AEP Source: Search domain: %s", domain)

        # Find records matching the criteria
        records = self.env["kpi_hub.record"].search(domain)

        _logger.info("KPI Hub AEP Source: Found %d records", len(records))

        if not records:
            _logger.warning(
                "No KPI Hub records found for template '%s', company %s, period %s-%s",
                self.template_id.name,
                company_id,
                date_from or "default",
                date_to or "default",
            )
            return 0.0

        # Calculate total value across all matching records
        total_value = 0.0

        for record in records:
            _logger.info(
                "KPI Hub AEP Source: Processing record: %s (period: %s to %s)",
                record.name,
                record.date_from,
                record.date_to,
            )

            # Find the specific item value for this KPI
            item_value = record.value_ids.filtered(lambda v: v.code == kpi_code)

            _logger.info(
                "KPI Hub AEP Source: Found %d item values for code '%s'",
                len(item_value),
                kpi_code,
            )

            if item_value:
                # For formula items, the value is already calculated
                # For data items, use the stored value
                value = item_value[0].value
                total_value += value

                _logger.info(
                    "Found KPI Hub value for '%s': %s (record: %s)",
                    kpi_code,
                    value,
                    record.name,
                )
            else:
                _logger.warning(
                    "No item value found for code '%s' in record '%s'",
                    kpi_code,
                    record.name,
                )

                # Debug: show all available codes in this record
                available_codes = [v.code for v in record.value_ids]
                _logger.info(
                    "Available codes in record '%s': %s", record.name, available_codes
                )

        _logger.info(
            "Total KPI Hub value for '%s': %s (from %s records)",
            kpi_code,
            total_value,
            len(records),
        )

        return total_value

    def _calculate_pro_rata_value(
        self, value, record_from, record_to, query_from, query_to
    ):
        """Calculate pro-rata value based on date overlap."""
        # Calculate overlap days
        overlap_start = max(record_from, query_from)
        overlap_end = min(record_to, query_to)

        if overlap_start > overlap_end:
            return 0.0

        overlap_days = (overlap_end - overlap_start).days + 1
        record_days = (record_to - record_from).days + 1

        if record_days == 0:
            return 0.0

        # Calculate pro-rata value
        pro_rata_value = value * (overlap_days / record_days)

        return pro_rata_value

    @api.model
    def parse_kpi_expression(self, expression):
        """Parse a KPI expression to extract code and optional date range.

        Args:
            expression (str): Expression like 'kpi[CODE]' or 'kpi[CODE][DATE_RANGE]'

        Returns:
            tuple: (kpi_code, date_range_id) or (None, None) if invalid
        """
        # Pattern: kpi[CODE] or kpi[CODE][DATE_RANGE]
        pattern = r"kpi\[([^\]]+)\](?:\[([^\]]+)\])?"
        match = re.match(pattern, expression)

        if not match:
            return None, None

        kpi_code = match.group(1).strip()
        date_range_name = match.group(2).strip() if match.group(2) else None

        # Find date range if specified
        date_range_id = None
        if date_range_name:
            date_range = self.env["date.range"].search(
                [
                    ("name", "=", date_range_name),
                ],
                limit=1,
            )
            if date_range:
                date_range_id = date_range.id
            else:
                _logger.warning(
                    "Date range '%s' not found for KPI expression '%s'",
                    date_range_name,
                    expression,
                )

        return kpi_code, date_range_id

    @api.model
    def evaluate_kpi_expression(self, expression, date_from, date_to, company_id=None):
        """Evaluate a KPI expression and return the value.

        Args:
            expression (str): KPI expression to evaluate
            date_from (date): Start date for the query
            date_to (date): End date for the query
            company_id (int): Company ID (optional)

        Returns:
            float: The evaluated KPI value
        """
        kpi_code, date_range_id = self.parse_kpi_expression(expression)

        if not kpi_code:
            _logger.warning("Invalid KPI expression: %s", expression)
            return 0.0

        # Use date range dates if specified
        if date_range_id:
            date_range = self.env["date.range"].browse(date_range_id)
            if date_range.exists():
                date_from = date_range.date_start
                date_to = date_range.date_end

        # Find the appropriate AEP source for this KPI
        source = self._find_source_for_kpi(kpi_code, company_id)

        if not source:
            _logger.warning(
                "No AEP source found for KPI code '%s' in company %s",
                kpi_code,
                company_id,
            )
            return 0.0

        # Get the value from the source
        return source.get_kpi_value(kpi_code, date_from, date_to, company_id)

    @api.model
    def _find_source_for_kpi(self, kpi_code, company_id=None):
        """Find the appropriate AEP source for a given KPI code."""
        # Search for sources that contain this KPI code
        sources = self.search(
            [
                ("active", "=", True),
                ("template_id.item_template_ids.code", "=", kpi_code),
            ]
        )

        if not sources:
            return None

        # Filter by company if specified
        if company_id:
            company_sources = sources.filtered(lambda s: s.company_id.id == company_id)
            if company_sources:
                return company_sources[0]

        # Return the first available source
        return sources[0]

    @api.model
    def get_available_kpi_codes(self, company_id=None):
        """Get all available KPI codes from active sources."""
        sources = self.search([("active", "=", True)])

        if company_id:
            sources = sources.filtered(lambda s: s.company_id.id == company_id)

        kpi_codes = set()
        for source in sources:
            item_codes = source.template_id.item_template_ids.mapped("code")
            kpi_codes.update(item_codes)

        return sorted(list(kpi_codes))

    @api.model
    def create_auto_mappings(self):
        """Create automatic mappings for all KPI items in active sources."""
        sources = self.search([("active", "=", True), ("auto_map_items", "=", True)])

        for source in sources:
            source._create_auto_mappings()

    def _create_auto_mappings(self):
        """Create automatic mappings for this source."""
        # This method would create mappings between KPI Hub items and MIS report KPIs
        # Implementation depends on your specific requirements
        pass

    @api.model
    def _extend_aep_processor(self, aep_processor):
        """Extend the AEP processor to handle KPI Hub expressions.

        This method is called by MIS Builder to extend the AEP with
        KPI Hub expression support.
        """
        # Get the extension model
        extension_model = self.env["mis.aep.extension"]

        # Extend the processor
        extended_processor = extension_model.extend_aep_processor(aep_processor)

        # Add KPI Hub specific methods to the processor
        def get_kpi_hub_value(kpi_code, date_from=None, date_to=None, company_id=None):
            """Get KPI Hub value for a specific KPI code."""
            # Find active AEP sources
            sources = self.env["kpi_hub.aep.source"].search([("active", "=", True)])

            total_value = 0.0
            for source in sources:
                value = source.get_kpi_value(kpi_code, date_from, date_to, company_id)
                total_value += value

            return total_value

        # Add the method to the processor
        aep_processor.get_kpi_hub_value = get_kpi_hub_value

        return extended_processor
