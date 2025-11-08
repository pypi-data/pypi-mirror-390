# KPI Data Hub - MIS Builder Integration

This document explains how to integrate KPI Data Hub with MIS Builder to create dynamic financial reports based on KPI formulas and data.

## Overview

The integration allows MIS Builder reports to use data from KPI Hub records, enabling:
- Dynamic KPI calculations based on formulas
- Hierarchical data structures
- Multi-company support
- Date range filtering
- Automatic formula recalculation

## Architecture

### 1. KPI Hub AEP Source (`kpi_hub.aep.source`)

This model provides a custom data source for the Accounting Expression Processor (AEP) that allows MIS reports to directly reference KPI Hub data using expressions like:
- `kpi[KPI_CODE]` - Basic KPI reference
- `kpi[KPI_CODE][DATE_RANGE]` - KPI with specific date range

### 2. MIS KPI Data Integration (`mis.kpi.data.integration`)

Extends the standard `mis.kpi.data` model to include KPI Hub data sources, allowing manual KPI data entries to be supplemented or replaced with KPI Hub data.

### 3. KPI Hub MIS Report (`kpi_hub.mis.report`)

Links KPI Hub templates with MIS reports and provides mapping between KPI Hub items and MIS report KPIs.

## Usage Examples

### 1. Basic KPI Expression

In a MIS report KPI expression, use:
```
kpi[REVENUE]
```

This will retrieve the value of the KPI with code "REVENUE" from the active KPI Hub template.

### 2. KPI with Date Range

```
kpi[PROFIT][Q1_2024]
```

This will retrieve the "PROFIT" KPI value for the "Q1_2024" date range.

### 3. Complex Formulas

You can combine KPI Hub expressions with standard accounting expressions:
```
kpi[REVENUE] + bal[70] - kpi[COSTS]
```

This adds KPI Hub revenue, adds account 70 balance, and subtracts KPI Hub costs.

## Setup Instructions

### 1. Create KPI Hub AEP Source

1. Go to **KPI Hub > MIS Integration > AEP Data Sources**
2. Create a new source:
   - **Name**: Descriptive name for the source
   - **Template**: Select the KPI Hub template to use
   - **Company**: Select the company (multi-company support)
   - **Expression Pattern**: Usually "kpi" (default)
   - **Auto-map Items**: Enable for automatic mapping

### 2. Configure MIS Report Integration

1. Go to **KPI Hub > MIS Integration > MIS Reports**
2. Create a new integration:
   - **Name**: Descriptive name
   - **KPI Hub Template**: Select the template
   - **MIS Report**: Select the MIS report to integrate with
   - **Company**: Select the company

### 3. Map KPI Items to MIS KPIs

1. In the MIS Report integration, go to the **Item Mappings** tab
2. Create mappings between KPI Hub items and MIS report KPIs
3. Optionally set multipliers and offsets for value transformation

### 4. Use KPI Expressions in MIS Reports

1. Go to your MIS report configuration
2. In KPI expressions, use the `kpi[CODE]` syntax
3. Save and test the report

## Advanced Features

### 1. Pro-rata Date Calculations

When KPI Hub records have different date ranges than the MIS report period, the system automatically calculates pro-rata values based on date overlap.

### 2. Multi-company Support

Each AEP source can be configured for a specific company, allowing different KPI data for different companies.

### 3. Formula Dependencies

KPI Hub automatically handles formula dependencies and calculates values in the correct order.

### 4. Validation

The system validates KPI expressions and provides warnings for:
- Missing KPI codes
- Invalid date ranges
- Company mismatches

## Troubleshooting

### Common Issues

1. **KPI Code Not Found**
   - Verify the KPI code exists in the selected template
   - Check that the template is active
   - Ensure the company matches

2. **Date Range Issues**
   - Verify date range names exist
   - Check date range validity

3. **No Data Returned**
   - Check if KPI Hub records exist for the period
   - Verify company matching
   - Check template activation status

### Debug Information

Enable debug logging to see detailed information about:
- KPI expression parsing
- Data retrieval
- Value calculations
- Date range processing

## Performance Considerations

1. **Indexing**: Ensure proper database indexes on date fields
2. **Caching**: KPI Hub values are calculated once and cached
3. **Batch Processing**: Large reports may benefit from batch processing
4. **Date Range Optimization**: Use specific date ranges when possible

## Best Practices

1. **Naming Conventions**: Use clear, consistent KPI codes
2. **Date Ranges**: Define standard date ranges for consistency
3. **Template Organization**: Group related KPIs in logical templates
4. **Company Separation**: Use separate templates for different companies when needed
5. **Formula Complexity**: Keep formulas simple and well-documented

## Example Templates

### Financial Performance Template

```
REVENUE (data) - Revenue from operations
COSTS (data) - Operating costs
PROFIT (formula: REVENUE - COSTS)
MARGIN (formula: (PROFIT / REVENUE) * 100)
```

### Balance Sheet Template

```
ASSETS (group)
  CURRENT_ASSETS (group)
    CASH (data)
    RECEIVABLES (data)
  FIXED_ASSETS (group)
    EQUIPMENT (data)
    BUILDINGS (data)
LIABILITIES (group)
  CURRENT_LIABILITIES (group)
    PAYABLES (data)
  LONG_TERM_DEBT (data)
EQUITY (formula: ASSETS - LIABILITIES)
```

## Support

For technical support or questions about the integration:
1. Check the logs for error messages
2. Verify all dependencies are installed
3. Test with simple expressions first
4. Contact the development team for complex issues
