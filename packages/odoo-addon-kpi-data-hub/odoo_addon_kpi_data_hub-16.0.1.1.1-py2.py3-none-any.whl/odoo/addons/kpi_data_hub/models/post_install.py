"""
Post-installation script for KPI Data Hub versioning system
"""

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def post_install_versioning_system(cr, registry):
    """Initialize versioning system after module installation"""
    env = api.Environment(cr, SUPERUSER_ID, {})

    try:
        # Update all existing templates to have version info if missing
        templates = env["kpi_hub.template"].search([])
        for template in templates:
            if not template.version_date:
                # Set version date for existing templates
                template.write(
                    {
                        "version_date": template.create_date or template.write_date,
                    }
                )

        # Update all existing records to capture template versions
        records = env["kpi_hub.record"].search([])
        for record in records:
            if not record.template_version and record.template_id:
                record.write(
                    {
                        "template_version": record.template_id.version,
                        "template_version_date": record.template_id.version_date,
                    }
                )

        cr.commit()
        _logger.info("KPI Data Hub versioning system initialized successfully")

    except Exception as e:
        cr.rollback()
        _logger.error(f"Error initializing versioning system: {e}")
        # Don't raise exception to avoid blocking module installation


def uninstall_versioning_cleanup(cr, registry):
    """Cleanup versioning data when module is uninstalled"""
    # This would be called during module uninstall if needed
    pass
