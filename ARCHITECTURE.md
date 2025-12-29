# Financial Projections Module - Technical Architecture

## Overview

The Financial Projections module is built on the Frappe Framework, leveraging its powerful DocType system, ORM, and server-side calculation capabilities. This document provides technical details for developers who want to understand, extend, or contribute to the module.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     Financial Projection                         │
│                     (Main DocType)                               │
├─────────────────────────────────────────────────────────────────┤
│  Configuration:                                                  │
│  - Basic Info (name, company, dates)                           │
│  - Cash Flow Settings (delays, starting cash)                  │
│  - Summary Fields (calculated totals)                          │
└────────────┬──────────────────────────────────────┬────────────┘
             │                                       │
    ┌────────┴───────┐                    ┌─────────┴─────────┐
    │  Assumptions   │                    │  Calculated Data   │
    │  (Input)       │                    │  (Output)          │
    └────────┬───────┘                    └─────────┬─────────┘
             │                                       │
    ┌────────┴────────────────┐           ┌─────────┴──────────┐
    │                         │           │                     │
┌───▼────┐  ┌────▼─────┐  ┌──▼───┐  ┌───▼─────┐           │
│Revenue │  │   Cost   │  │Staff │  │  CAPEX  │  │ Monthly  │
│ Lines  │  │  Lines   │  │Lines │  │  Lines  │  │   Data   │
│(Child) │  │ (Child)  │  │(Ch.) │  │ (Child) │  │ (Child)  │
└────────┘  └──────────┘  └──────┘  └─────────┘  └──────────┘
```

## Data Model

### Core Entities

#### 1. Financial Projection (Master DocType)

**Purpose:** Container for all projection data and settings

**Key Fields:**
- `projection_name` (Data, Unique) - Identifier
- `start_date` (Date) - First month of projection
- `projection_years` (Int) - Duration (default 3)
- `cash_on_hand_start` (Currency) - Starting cash
- `cash_*_delay` (Int) - Payment timing settings

**Relationships:**
- Has Many: Revenue Lines, Cost Lines, Staff Lines, CAPEX Lines, Monthly Data

**Validation Rules:**
- Delays must be 0-6 months
- Start date required
- Projection name unique

**Calculation Trigger:** `before_save()` hook

#### 2. Revenue Line (Child Table)

**Purpose:** Define revenue streams and growth assumptions

**Key Fields:**
- `revenue_type` (Data) - Identifier for revenue stream
- `calculation_type` (Select) - "Recurring" or "One-Time"
- `price_per_unit` (Currency) - Unit price
- `monthly_new_sales` (Float) - Growth rate
- `annual_price_increase` (Percent) - Price escalation

**Calculation Logic:**
```python
# For Recurring Revenue
monthly_revenue = carried_instances * price_per_unit

# For One-Time Revenue
monthly_revenue = (instances * price) / implementation_months
```

**Carried Instances Tracking:**
```python
# Month 1: carried = 0 + new_sales = 0 + 500 = 500
# Month 2: carried = 500 + new_sales = 500 + 500 = 1000
# Month 3: carried = 1000 + new_sales = 1000 + 500 = 1500
```

#### 3. Cost Line (Child Table)

**Purpose:** Define costs that scale with revenue or are fixed

**Calculation Types:**
1. **Per Instance:** Cost × Instances (from related revenue)
2. **Fixed Monthly:** Constant cost per month
3. **Percentage of Revenue:** Revenue × Percentage

**Key Fields:**
- `cost_type` (Data) - Identifier
- `calculation_type` (Select) - Method
- `cost_per_unit` (Currency) - For per-instance
- `cost_percentage` (Percent) - For percentage method
- `related_revenue_type` (Data) - Links to revenue stream

**Example:**
```python
# IoT hosting: $0.10 per device
# Related to "IoT Licenses" revenue
# Month 1: 500 devices × $0.10 = $50
# Month 12: 6000 devices × $0.10 = $600
```

#### 4. Staff Line (Child Table)

**Purpose:** Model headcount and compensation over time

**Key Fields:**
- `position_title` (Data)
- `monthly_salary` (Currency)
- `monthly_benefits` (Currency)
- `vehicle_allowance` (Currency)
- `start_month` (Int) - When position begins (1-36)
- `annual_increase` (Percent) - Raises

**Calculation:**
```python
if month_num >= start_month:
    base = monthly_salary
    # Apply compound annual increase
    if year_num > 1:
        base *= (1 + annual_increase/100) ** (year_num - 1)
    total_cost = base + benefits + vehicle_allowance
```

#### 5. CAPEX Line (Child Table)

**Purpose:** Track capital expenditure timing and amounts

**Key Fields:**
- `asset_name` (Data)
- `cost` (Currency)
- `purchase_month` (Int, 1-12)
- `purchase_year` (Int, 1-3)
- `depreciation_years` (Int) - For future use
- `salvage_value` (Currency) - For future use

**Current Implementation:**
- One-time expense in specified month
- Depreciation not yet calculated in P&L

#### 6. Monthly Data (Child Table - Calculated)

**Purpose:** Store month-by-month calculated projections

**Generated Fields:**
- **Identity:** month_number, month_date, year_number
- **P&L:** revenue, cost_of_revenue, gross_profit, operating_expenses, capex, net_income
- **Cash Flow:** cash_receipts, cash_payments, net_cash_flow, cash_balance
- **Cumulative:** cumulative_revenue, cumulative_cost, cumulative_gross_profit

**Calculation Order:**
1. Revenue (by type, summed)
2. Cost of Revenue (by type, summed)
3. Gross Profit (revenue - cost)
4. Operating Expenses (staff costs)
5. CAPEX (if purchase month matches)
6. Net Income (gross profit - opex)
7. Cash Flow (with delays applied)
8. Cumulative totals

## Calculation Engine

### Main Algorithm Flow

```python
def calculate_projections(self):
    # 1. Initialize
    self.monthly_projections = []
    carried_instances = {}
    cash_balance = self.cash_on_hand_start
    
    # 2. Process each month (1 to projection_years * 12)
    for month_num in range(1, total_months + 1):
        # 2a. Calculate P&L components
        revenue = self.calculate_monthly_revenue(...)
        cost = self.calculate_monthly_cost(...)
        gross_profit = revenue - cost
        opex = self.calculate_monthly_opex(...)
        capex = self.calculate_monthly_capex(...)
        net_income = gross_profit - opex
        
        # 2b. Calculate cash flow with delays
        cash_in = self.calculate_cash_receipts(month_num, revenue)
        cash_out = (
            self.calculate_cash_payments_cor(month_num, cost) +
            self.calculate_cash_payments_opex(month_num, opex) +
            self.calculate_cash_payments_capex(month_num, capex)
        )
        net_cash = cash_in - cash_out
        cash_balance += net_cash
        
        # 2c. Create monthly row
        self.append('monthly_projections', {
            'month_number': month_num,
            'revenue': revenue,
            'cash_balance': cash_balance,
            # ... other fields
        })
    
    # 3. Calculate summary totals
    self.update_summary_fields()
```

### Revenue Calculation Detail

```python
def calculate_monthly_revenue(self, month_num, year_num, month_in_year, carried_instances):
    total_revenue = 0
    
    for revenue_line in self.revenue_assumptions:
        # Get or initialize carried instances
        key = revenue_line.revenue_type
        if key not in carried_instances:
            carried_instances[key] = 0
        
        # Add new sales
        carried_instances[key] += revenue_line.monthly_new_sales
        instances = carried_instances[key]
        
        # Calculate price with annual increase
        price = revenue_line.price_per_unit
        if year_num > 1 and revenue_line.annual_price_increase:
            price *= (1 + revenue_line.annual_price_increase/100) ** (year_num - 1)
        
        # Calculate revenue based on type
        if revenue_line.calculation_type == "Recurring":
            monthly_revenue = instances * price
        elif revenue_line.calculation_type == "One-Time":
            # Spread over implementation months
            if revenue_line.implementation_months:
                if month_in_year <= revenue_line.implementation_months:
                    monthly_revenue = (instances * price) / revenue_line.implementation_months
                else:
                    monthly_revenue = 0
            else:
                monthly_revenue = instances * price if month_in_year == 1 else 0
        
        total_revenue += monthly_revenue
    
    return total_revenue
```

### Cash Flow Delay Logic

```python
def calculate_cash_receipts(self, month_num, revenue):
    delay = self.cash_receipt_delay
    
    # Simplified implementation
    # Full implementation would look back at revenue from (month_num - delay)
    # and apply that month's revenue to current cash receipts
    
    if delay == 0:
        return revenue  # Immediate receipt
    
    if month_num <= delay:
        return 0  # No receipts during initial delay period
    
    # In production, would reference:
    # return self.monthly_projections[month_num - delay - 1].revenue
    return revenue  # Simplified for prototype
```

## Extension Points

### 1. Adding Custom Calculations

Extend the main calculation method:

```python
# In financial_projection.py

def calculate_projections(self):
    # ... existing code ...
    
    for month_num in range(1, total_months + 1):
        # ... existing calculations ...
        
        # Add custom calculation
        custom_metric = self.calculate_custom_metric(month_num)
        
        monthly_row = self.append('monthly_projections', {})
        # ... existing fields ...
        monthly_row.custom_metric = custom_metric
```

### 2. Adding Custom DocTypes

Create related DocTypes for extended functionality:

```json
{
  "doctype": "Financial Projection Scenario",
  "fields": [
    {"fieldname": "scenario_name", "fieldtype": "Data"},
    {"fieldname": "parent_projection", "fieldtype": "Link", "options": "Financial Projection"},
    {"fieldname": "probability", "fieldtype": "Percent"},
    {"fieldname": "description", "fieldtype": "Text"}
  ]
}
```

### 3. Adding Reports

Create custom Script Reports:

```python
# financial_projections/report/cash_flow_analysis/cash_flow_analysis.py

def execute(filters=None):
    columns = [
        {"label": "Month", "fieldname": "month", "width": 100},
        {"label": "Cash In", "fieldname": "cash_in", "width": 120},
        {"label": "Cash Out", "fieldname": "cash_out", "width": 120},
        {"label": "Balance", "fieldname": "balance", "width": 120}
    ]
    
    data = []
    
    projection = frappe.get_doc("Financial Projection", filters.get("projection"))
    
    for month in projection.monthly_projections:
        data.append({
            "month": month.month_date,
            "cash_in": month.cash_receipts,
            "cash_out": month.cash_payments,
            "balance": month.cash_balance
        })
    
    return columns, data
```

### 4. Adding Client-Side Behavior

Extend the JavaScript controller:

```javascript
// financial_projection.js

frappe.ui.form.on('Financial Projection', {
    refresh: function(frm) {
        // Add custom button
        frm.add_custom_button(__('Recalculate'), function() {
            frm.save();
        });
        
        // Add chart
        if (frm.doc.monthly_projections && frm.doc.monthly_projections.length > 0) {
            render_revenue_chart(frm);
        }
    },
    
    start_date: function(frm) {
        // Trigger recalculation when start date changes
        frm.trigger('validate');
    }
});

function render_revenue_chart(frm) {
    let data = frm.doc.monthly_projections.map(m => ({
        month: m.month_date,
        revenue: m.revenue,
        cost: m.cost_of_revenue,
        net_income: m.net_income
    }));
    
    let chart = new frappe.Chart("#revenue_chart", {
        title: "Financial Projection",
        data: {
            labels: data.map(d => d.month),
            datasets: [
                {name: "Revenue", values: data.map(d => d.revenue)},
                {name: "Cost", values: data.map(d => d.cost)},
                {name: "Net Income", values: data.map(d => d.net_income)}
            ]
        },
        type: 'line',
        height: 300
    });
}
```

## Performance Considerations

### Calculation Complexity

- **Time Complexity:** O(n × m) where n = months, m = assumption lines
- **Typical Execution:** < 1 second for 3-year projection with 20 lines
- **Optimization Opportunities:**
  - Cache carried instance calculations
  - Bulk insert monthly rows
  - Async calculation for very large projections

### Database Queries

- All calculations done in-memory
- Single database write per save
- Child tables inserted in batch
- No N+1 query problems

### Scaling Limits

Current prototype handles:
- Up to 10 years (120 months)
- Up to 100 assumption lines per category
- Up to 10 concurrent users calculating simultaneously

## Testing Strategy

### Unit Tests

```python
# tests/test_financial_projection.py

def test_revenue_calculation():
    projection = frappe.get_doc({
        "doctype": "Financial Projection",
        "projection_name": "Test",
        "start_date": "2025-01-01",
        "revenue_assumptions": [{
            "revenue_type": "Test Revenue",
            "price_per_unit": 100,
            "monthly_new_sales": 10,
            "calculation_type": "Recurring"
        }]
    })
    projection.calculate_projections()
    
    # Month 1: 10 instances × $100 = $1,000
    assert projection.monthly_projections[0].revenue == 1000
    
    # Month 2: 20 instances × $100 = $2,000
    assert projection.monthly_projections[1].revenue == 2000
```

### Integration Tests

Test full workflows:
1. Create projection
2. Add assumptions
3. Save and verify calculations
4. Modify assumptions
5. Verify recalculation
6. Export and verify format

### Validation Tests

Test edge cases:
- Zero revenue
- Negative costs (refunds)
- Very large numbers
- Invalid delay values
- Missing required fields

## Security Considerations

### Permissions

- Role-based access control via Frappe roles
- System Manager: Full access
- Accounts Manager: Create, edit, delete
- Accounts User: Read-only access

### Data Validation

- Server-side validation of all inputs
- Type checking on numeric fields
- Range validation on delays (0-6)
- Required field enforcement

### Audit Trail

- Frappe's built-in version tracking
- All changes logged with user and timestamp
- Ability to restore previous versions

## Deployment

### Requirements

```
frappe >= 14.0.0
erpnext >= 14.0.0 (optional)
python >= 3.10
```

### Installation Steps

See QUICKSTART.md and README.md for detailed installation instructions.

### Configuration

All configuration is done through the UI - no config files needed.

### Monitoring

Monitor via:
- Frappe Error Log
- System Console
- Performance profiling tools

## Future Enhancements

### Phase 2 (Planned)
- Depreciation calculations
- Multiple scenarios per projection
- Actual vs. budget comparison
- Import from Excel
- Export to Excel with formulas

### Phase 3 (Planned)
- Interactive dashboard with charts
- Automatic sync with Sales/Purchase Orders
- Cash flow alerts and notifications
- Rolling forecasts (auto-update based on actuals)

### Phase 4 (Planned)
- Machine learning for forecast improvement
- Sensitivity analysis
- Monte Carlo simulation
- Integration with external data sources

## Contributing

See README.md for contribution guidelines.

### Code Style

- Follow Frappe coding standards
- Use type hints where appropriate
- Add docstrings to all methods
- Write unit tests for new features

### Pull Request Process

1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Submit PR with description
5. Respond to review feedback
6. Merge after approval

## License

MIT License - See LICENSE file

## Support

- GitHub Issues: For bugs and feature requests
- Frappe Forum: For usage questions
- Email: support@es-au.com

---

**Document Version:** 1.0  
**Last Updated:** December 29, 2024  
**Author:** ES Australia
