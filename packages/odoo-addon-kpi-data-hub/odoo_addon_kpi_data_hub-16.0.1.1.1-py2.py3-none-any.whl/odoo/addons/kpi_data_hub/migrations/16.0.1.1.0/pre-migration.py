import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Assign codes to existing KPI data records using raw SQL."""
    # Add column if not exists
    cr.execute(
        """
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'kpi_hub_record' AND column_name = 'code'"""
    )
    if not cr.fetchone():
        cr.execute("ALTER TABLE kpi_hub_record ADD COLUMN code VARCHAR")
        _logger.info("Column 'code' added to 'kpi_hub_record' table.")

    # Ensure sequence exists before using it
    cr.execute("SELECT 1 FROM ir_sequence WHERE code = 'kpi_hub.record'")
    if not cr.fetchone():
        cr.execute(
            """
            INSERT INTO ir_sequence (name, code, prefix, padding, number_next, number_increment, company_id)
            VALUES ('KPI Hub Record', 'kpi_hub.record', 'REC-', 5, 1, 1, NULL)
        """
        )
        _logger.info("Sequence 'kpi_hub.record' created.")

    env = api.Environment(cr, SUPERUSER_ID, {})
    sequence_model = env["ir.sequence"]

    cr.execute("SELECT id FROM kpi_hub_record WHERE code IS NULL OR code = ''")
    record_ids = [r[0] for r in cr.fetchall()]

    if not record_ids:
        _logger.info("No KPI records without a code found. Skipping migration.")
        return

    _logger.info(
        f"Found {len(record_ids)} KPI records without a code. Assigning codes..."
    )

    for record_id in record_ids:
        new_code = sequence_model.next_by_code("kpi_hub.record")
        cr.execute(
            "UPDATE kpi_hub_record SET code = %s WHERE id = %s", (new_code, record_id)
        )

    _logger.info("Finished assigning codes to existing KPI records.")
