import logging

from odoo import models

_logger = logging.getLogger(__name__)

_logger.info("KPI Data Hub: Loading mis_aep_extension.py")


class MisReportExtension(models.Model):
    _inherit = "mis.report"

    def prepare_locals_dict(self, date_from=None, date_to=None):
        _logger.info(
            "KPI Data Hub: prepare_locals_dict called with dates: %s to %s",
            date_from,
            date_to,
        )
        res = super().prepare_locals_dict()

        # Store dates in the environment context for later use
        if date_from and date_to:
            self = self.with_context(
                kpi_hub_date_from=date_from, kpi_hub_date_to=date_to
            )

        # Add our custom kpi function to the locals dict
        res["kpi"] = self._kpi_function
        _logger.info(
            "KPI Data Hub: 'kpi' function added to locals dict: %s", list(res.keys())
        )

        return res

    def _kpi_function(self, kpi_code):
        # Get dates from context if available
        date_from = self.env.context.get("kpi_hub_date_from")
        date_to = self.env.context.get("kpi_hub_date_to")

        _logger.info(
            "KPI Data Hub: _kpi_function called with code: %s, context dates: %s to %s",
            kpi_code,
            date_from,
            date_to,
        )

        # Get the current company from the environment
        company_id = self.env.company.id
        _logger.info("KPI Data Hub: Using company ID: %s", company_id)

        # Use context dates or fallback to current month
        if not date_from or not date_to:
            from datetime import datetime

            today = datetime.now().date()
            date_from = today.replace(day=1)  # First day of current month
            date_to = today
            _logger.info(
                "KPI Data Hub: Using fallback date range from %s to %s",
                date_from,
                date_to,
            )
        else:
            _logger.info(
                "KPI Data Hub: Using context date range from %s to %s",
                date_from,
                date_to,
            )

        # Now, let's call the logic from kpi_hub.aep.source
        aep_source_model = self.env["kpi_hub.aep.source"]

        # Find the right aep_source for the given kpi_code
        source = aep_source_model._find_source_for_kpi(kpi_code, company_id)
        if not source:
            _logger.warning(
                "KPI Data Hub: No KPI Hub AEP source found for KPI '%s' in company %s",
                kpi_code,
                company_id,
            )
            return 0.0

        _logger.info("KPI Data Hub: Using AEP source: %s", source.name)

        value = source.get_kpi_value(kpi_code, date_from, date_to, company_id)
        _logger.info("KPI Data Hub: Evaluated value for %s is %s", kpi_code, value)
        return value
