# Copyright 2025 Nicolás Ramos
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestItemValueDeletion(TransactionCase):
    """Test cases for KPI Hub Item Value deletion functionality"""

    def setUp(self):
        super().setUp()

        # Create a test template
        self.template = self.env["kpi_hub.template"].create(
            {
                "name": "Test Template for Deletion",
                "code": "TEST_DEL",
                "description": "Template to test item deletion",
            }
        )

        # Create test items with different configurations
        self.item_required = self.env["kpi_hub.item.template"].create(
            {
                "template_id": self.template.id,
                "name": "Required Item",
                "code": "REQ_ITEM",
                "calculation_type": "manual",
                "is_required": True,
                "sequence": 10,
            }
        )

        self.item_optional = self.env["kpi_hub.item.template"].create(
            {
                "template_id": self.template.id,
                "name": "Optional Item",
                "code": "OPT_ITEM",
                "calculation_type": "manual",
                "is_required": False,
                "sequence": 20,
            }
        )

        self.item_formula = self.env["kpi_hub.item.template"].create(
            {
                "template_id": self.template.id,
                "name": "Calculated Item",
                "code": "CALC_ITEM",
                "calculation_type": "formula",
                "formula": "REQ_ITEM + OPT_ITEM",
                "is_required": False,
                "sequence": 30,
            }
        )

        self.item_group = self.env["kpi_hub.item.template"].create(
            {
                "template_id": self.template.id,
                "name": "Group Item",
                "code": "GRP_ITEM",
                "calculation_type": "group",
                "is_group": True,
                "auto_sum_children": True,
                "is_required": False,
                "sequence": 40,
            }
        )

        # Create a test entity
        self.entity = self.env["kpi_hub.entity"].create(
            {
                "name": "Test Entity",
                "code": "TEST_ENT",
                "entity_type": "department",
            }
        )

        # Create a test date range
        self.date_range = self.env["date.range"].create(
            {
                "name": "Test Q1 2025",
                "type_id": self.env.ref("date_range.date_range_quarter").id,
                "date_start": "2025-01-01",
                "date_end": "2025-03-31",
            }
        )

        # Create a test record
        self.record = self.env["kpi_hub.record"].create(
            {
                "template_id": self.template.id,
                "entity_id": self.entity.id,
                "date_range_id": self.date_range.id,
                "date_from": "2025-01-01",
                "date_to": "2025-03-31",
            }
        )

        # Get the created item values
        self.value_required = self.record.item_value_ids.filtered(
            lambda v: v.code == "REQ_ITEM"
        )
        self.value_optional = self.record.item_value_ids.filtered(
            lambda v: v.code == "OPT_ITEM"
        )
        self.value_formula = self.record.item_value_ids.filtered(
            lambda v: v.code == "CALC_ITEM"
        )
        self.value_group = self.record.item_value_ids.filtered(
            lambda v: v.code == "GRP_ITEM"
        )

    def test_01_delete_optional_item_success(self):
        """Test that optional items can be deleted successfully"""
        # Set value to avoid required validation
        self.value_optional.value = 100.0

        # Should not raise any error
        self.value_optional.unlink()

        # Verify the item was deleted
        remaining_values = self.record.item_value_ids.filtered(
            lambda v: v.code == "OPT_ITEM"
        )
        self.assertEqual(len(remaining_values), 0, "Optional item should be deleted")

    def test_02_delete_required_item_success(self):
        """Test that required items CAN be deleted (new behavior)"""
        # Set value to avoid required validation during creation
        self.value_required.value = 100.0

        # Should not raise any error (changed behavior)
        self.value_required.unlink()

        # Verify the item WAS deleted
        remaining_values = self.record.item_value_ids.filtered(
            lambda v: v.code == "REQ_ITEM"
        )
        self.assertEqual(len(remaining_values), 0, "Required item CAN now be deleted")

    def test_03_delete_formula_item_fails(self):
        """Test that formula items cannot be deleted"""
        # Should raise ValidationError
        with self.assertRaises(ValidationError) as context:
            self.value_formula.unlink()

        # Verify error message
        self.assertIn("calculated/group item", str(context.exception))

        # Verify the item was NOT deleted
        remaining_values = self.record.item_value_ids.filtered(
            lambda v: v.code == "CALC_ITEM"
        )
        self.assertEqual(len(remaining_values), 1, "Formula item should NOT be deleted")

    def test_04_delete_group_item_fails(self):
        """Test that group items cannot be deleted"""
        # Should raise ValidationError
        with self.assertRaises(ValidationError) as context:
            self.value_group.unlink()

        # Verify error message
        self.assertIn("calculated/group item", str(context.exception))

        # Verify the item was NOT deleted
        remaining_values = self.record.item_value_ids.filtered(
            lambda v: v.code == "GRP_ITEM"
        )
        self.assertEqual(len(remaining_values), 1, "Group item should NOT be deleted")

    def test_05_delete_during_install_mode(self):
        """Test that deletion validations are skipped during install mode"""
        # This simulates the context during module installation
        with self.env.cr.savepoint():
            # Even formula items should be deletable in install_mode
            self.value_formula.with_context(install_mode=True).unlink()

            # Verify the item was deleted (in the savepoint)
            remaining_values = self.record.item_value_ids.filtered(
                lambda v: v.code == "CALC_ITEM"
            )
            self.assertEqual(
                len(remaining_values),
                0,
                "Formula item should be deleted in install_mode",
            )

    def test_06_delete_multiple_optional_items(self):
        """Test that multiple optional items can be deleted at once"""
        # Create additional optional items
        item_optional_2 = self.env["kpi_hub.item.template"].create(
            {
                "template_id": self.template.id,
                "name": "Optional Item 2",
                "code": "OPT_ITEM_2",
                "calculation_type": "manual",
                "is_required": False,
                "sequence": 50,
            }
        )

        # Sync record to create the new item value
        self.record.action_sync_with_template()

        # Get the optional values
        optional_values = self.record.item_value_ids.filtered(
            lambda v: v.code in ["OPT_ITEM", "OPT_ITEM_2"]
        )

        # Should not raise any error
        optional_values.unlink()

        # Verify both items were deleted
        remaining_values = self.record.item_value_ids.filtered(
            lambda v: v.code in ["OPT_ITEM", "OPT_ITEM_2"]
        )
        self.assertEqual(
            len(remaining_values), 0, "Both optional items should be deleted"
        )

    def test_07_record_still_valid_after_item_deletion(self):
        """Test that record remains valid after deleting items"""
        # Set item values
        self.value_required.value = 100.0
        self.value_optional.value = 50.0

        # Delete both optional and required items (now allowed)
        (self.value_optional | self.value_required).unlink()

        # Record should still exist
        self.assertTrue(self.record.exists(), "Record should still exist")

        # Both items should be deleted
        remaining_items = self.record.item_value_ids.filtered(
            lambda v: v.code in ["REQ_ITEM", "OPT_ITEM"]
        )
        self.assertEqual(len(remaining_items), 0, "Both items should be deleted")

    def test_08_group_calculation_sums_children(self):
        """Test that group items automatically sum their children values"""
        # Create a parent group item
        parent_group = self.env["kpi_hub.item.template"].create(
            {
                "template_id": self.template.id,
                "name": "Parent Group",
                "code": "PARENT_GRP",
                "calculation_type": "group",
                "sequence": 5,
            }
        )

        # Create child items under the parent
        child1 = self.env["kpi_hub.item.template"].create(
            {
                "template_id": self.template.id,
                "name": "Child 1",
                "code": "CHILD1",
                "calculation_type": "data",
                "parent_id": parent_group.id,
                "sequence": 6,
            }
        )

        child2 = self.env["kpi_hub.item.template"].create(
            {
                "template_id": self.template.id,
                "name": "Child 2",
                "code": "CHILD2",
                "calculation_type": "data",
                "parent_id": parent_group.id,
                "sequence": 7,
            }
        )

        child3 = self.env["kpi_hub.item.template"].create(
            {
                "template_id": self.template.id,
                "name": "Child 3",
                "code": "CHILD3",
                "calculation_type": "data",
                "parent_id": parent_group.id,
                "sequence": 8,
            }
        )

        # Sync record to create the new item values
        self.record.action_sync_with_template()

        # Get the item values
        parent_value = self.record.item_value_ids.filtered(
            lambda v: v.code == "PARENT_GRP"
        )
        child1_value = self.record.item_value_ids.filtered(lambda v: v.code == "CHILD1")
        child2_value = self.record.item_value_ids.filtered(lambda v: v.code == "CHILD2")
        child3_value = self.record.item_value_ids.filtered(lambda v: v.code == "CHILD3")

        # Verify items were created
        self.assertTrue(parent_value, "Parent group item value should exist")
        self.assertTrue(child1_value, "Child1 item value should exist")
        self.assertTrue(child2_value, "Child2 item value should exist")
        self.assertTrue(child3_value, "Child3 item value should exist")

        # Set values for children
        child1_value.value = 100.0
        child2_value.value = 200.0
        child3_value.value = 50.0

        # Initially parent should be 0 (no calculation done yet)
        self.assertEqual(parent_value.value, 0.0, "Parent should start at 0")

        # Calculate formulas (this should now include groups)
        self.record.action_calculate_formulas()

        # Parent should now be sum of children: 100 + 200 + 50 = 350
        self.assertEqual(
            parent_value.value,
            350.0,
            "Parent group should sum children values (100 + 200 + 50 = 350)",
        )

    def test_09_group_calculation_nested_hierarchy(self):
        """Test that group calculation works with nested hierarchies"""
        # Create top-level group
        top_group = self.env["kpi_hub.item.template"].create(
            {
                "template_id": self.template.id,
                "name": "Top Level Group",
                "code": "TOP_GRP",
                "calculation_type": "group",
                "sequence": 1,
            }
        )

        # Create mid-level group under top
        mid_group = self.env["kpi_hub.item.template"].create(
            {
                "template_id": self.template.id,
                "name": "Mid Level Group",
                "code": "MID_GRP",
                "calculation_type": "group",
                "parent_id": top_group.id,
                "sequence": 2,
            }
        )

        # Create leaf children under mid-group
        leaf1 = self.env["kpi_hub.item.template"].create(
            {
                "template_id": self.template.id,
                "name": "Leaf 1",
                "code": "LEAF1",
                "calculation_type": "data",
                "parent_id": mid_group.id,
                "sequence": 3,
            }
        )

        leaf2 = self.env["kpi_hub.item.template"].create(
            {
                "template_id": self.template.id,
                "name": "Leaf 2",
                "code": "LEAF2",
                "calculation_type": "data",
                "parent_id": mid_group.id,
                "sequence": 4,
            }
        )

        # Sync record
        self.record.action_sync_with_template()

        # Get item values
        top_value = self.record.item_value_ids.filtered(lambda v: v.code == "TOP_GRP")
        mid_value = self.record.item_value_ids.filtered(lambda v: v.code == "MID_GRP")
        leaf1_value = self.record.item_value_ids.filtered(lambda v: v.code == "LEAF1")
        leaf2_value = self.record.item_value_ids.filtered(lambda v: v.code == "LEAF2")

        # Set leaf values
        leaf1_value.value = 75.0
        leaf2_value.value = 25.0

        # Calculate formulas
        self.record.action_calculate_formulas()

        # Mid-group should sum its direct children: 75 + 25 = 100
        self.assertEqual(
            mid_value.value,
            100.0,
            "Mid-level group should sum direct children (75 + 25 = 100)",
        )

        # Top-group should sum its direct children (which includes mid-group): 100
        self.assertEqual(
            top_value.value,
            100.0,
            "Top-level group should sum direct children (mid-group = 100)",
        )

    def test_10_group_calculation_empty_children(self):
        """Test group calculation with no children or all zero children"""
        # Create a group with no children initially
        empty_group = self.env["kpi_hub.item.template"].create(
            {
                "template_id": self.template.id,
                "name": "Empty Group",
                "code": "EMPTY_GRP",
                "calculation_type": "group",
                "sequence": 60,
            }
        )

        # Sync record
        self.record.action_sync_with_template()

        # Get the group value
        empty_value = self.record.item_value_ids.filtered(
            lambda v: v.code == "EMPTY_GRP"
        )

        # Calculate formulas
        self.record.action_calculate_formulas()

        # Group with no children should be 0
        self.assertEqual(empty_value.value, 0.0, "Group with no children should be 0")

        # Now add children with zero values
        child_zero1 = self.env["kpi_hub.item.template"].create(
            {
                "template_id": self.template.id,
                "name": "Zero Child 1",
                "code": "ZERO1",
                "calculation_type": "data",
                "parent_id": empty_group.id,
                "sequence": 61,
            }
        )

        child_zero2 = self.env["kpi_hub.item.template"].create(
            {
                "template_id": self.template.id,
                "name": "Zero Child 2",
                "code": "ZERO2",
                "calculation_type": "data",
                "parent_id": empty_group.id,
                "sequence": 62,
            }
        )

        # Sync again
        self.record.action_sync_with_template()

        # Get updated values
        zero1_value = self.record.item_value_ids.filtered(lambda v: v.code == "ZERO1")
        zero2_value = self.record.item_value_ids.filtered(lambda v: v.code == "ZERO2")

        # Keep zero values (default)
        zero1_value.value = 0.0
        zero2_value.value = 0.0

        # Calculate formulas
        self.record.action_calculate_formulas()

        # Group should still be 0
        self.assertEqual(
            empty_value.value, 0.0, "Group with zero-valued children should be 0"
        )
