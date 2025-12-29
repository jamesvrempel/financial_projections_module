# Financial Projections Module for Frappe/ERPNext

## Overview

The Financial Projections module is a comprehensive financial planning and forecasting tool for ERPNext. It allows organizations to create detailed 3-year financial projections including:

- **Revenue Projections** - Software licenses, services, and recurring revenue
- **Cost of Revenue** - Instance-based costs, hosting fees, and service costs
- **Operating Expenses** - Staff salaries, benefits, and overhead
- **Capital Expenditures** - Equipment, furniture, and infrastructure investments
- **Cash Flow Management** - With configurable payment and receipt delays
- **Monthly P&L Tracking** - Detailed month-by-month profit and loss statements

## Features

### Core Capabilities

1. **Flexible Revenue Modeling**
   - Recurring monthly revenue (subscriptions, licenses)
   - One-time project revenue
   - Volume-based pricing with growth tracking
   - Annual price increases
   - Carried-forward customer base tracking

2. **Comprehensive Cost Tracking**
   - Per-instance costs (follows revenue volume)
   - Fixed monthly costs
   - Percentage-based costs (% of revenue)
   - Multiple cost categories

3. **Staff Planning**
   - Position-by-position modeling
   - Salary, benefits, and allowances
   - Staggered start dates
   - Annual salary increases
   - Department tracking

4. **CAPEX Management**
   - Asset purchase tracking
   - Depreciation schedules
   - Category-based organization
   - Multi-year planning

5. **Cash Flow Projections**
   - Configurable payment delays (0-6 months)
   - Cash receipt delays
   - Cash balance tracking
   - Alert thresholds

6. **Automated Calculations**
   - Monthly P&L generation
   - Cumulative totals tracking
   - Year-by-year summaries
   - Gross profit and net income calculations

## Installation

### Prerequisites

- Frappe Framework (v14 or higher)
- ERPNext (v14 or higher) - optional but recommended

### Installation Steps

1. **Navigate to your Frappe bench directory:**
   ```bash
   cd /path/to/your/frappe-bench
   ```

2. **Get the app:**
   ```bash
   bench get-app /path/to/financial_projections_module
   ```

3. **Install on your site:**
   ```bash
   bench --site your-site-name install-app financial_projections
   ```

4. **Run migrations:**
   ```bash
   bench --site your-site-name migrate
   ```

5. **Restart bench:**
   ```bash
   bench restart
   ```

### Alternative: Manual Installation

If you want to manually copy files:

1. Copy the entire `financial_projections` directory to:
   ```
   frappe-bench/apps/financial_projections/
   ```

2. Add to your site's `apps.txt`:
   ```bash
   echo "financial_projections" >> sites/your-site-name/apps.txt
   ```

3. Run the installation commands above (steps 4-5)

## Usage

### Creating Your First Projection

1. **Navigate to Financial Projections**
   - Open ERPNext
   - Search for "Financial Projection" in the search bar
   - Click "New"

2. **Enter Basic Information**
   - Projection Name: "FY2025 Budget"
   - Company: Select your company
   - Start Date: First month of projection period
   - Projection Years: 3 (default)
   - Cash on Hand (Start): Your starting cash balance

3. **Configure Cash Flow Assumptions**
   - Cash Receipt Delay: How many months after sale before you receive payment (e.g., 1 for Net-30 terms)
   - Cost of Revenue Delay: Payment terms with suppliers (e.g., 1 month)
   - OPEX Delay: When you pay operating expenses (usually 0)
   - CAPEX Delay: When you pay for capital purchases (0-6 months)

4. **Add Revenue Assumptions**
   Click "Add Row" in Revenue Lines section:
   - Revenue Type: "IoT Licenses"
   - Calculation Type: "Recurring"
   - Price per Unit/Month: 10.00
   - Monthly New Sales: 500 (new customers/devices per month)
   - Annual Price Increase %: 0

5. **Add Cost Assumptions**
   Click "Add Row" in Cost Lines section:
   - Cost Type: "IoT Platform Hosting"
   - Calculation Type: "Per Instance"
   - Cost per Unit: 0.10
   - Related Revenue Type: "IoT Licenses"

6. **Add Staff Positions**
   Click "Add Row" in Staff Positions section:
   - Position Title: "CEO"
   - Monthly Salary: 5000.00
   - Monthly Benefits: 0
   - Start Month: 1
   - Annual Increase %: 10

7. **Add CAPEX Items** (Optional)
   Click "Add Row" in Capital Expenditures section:
   - Asset Name: "Business Laptop"
   - Asset Category: "Office Equipment"
   - Cost: 2000.00
   - Purchase Month: 4
   - Purchase Year: 1

8. **Save**
   - Click "Save" button
   - The system will automatically calculate all monthly projections
   - Review the Monthly Projections table for detailed month-by-month data
   - Check the Summary section for yearly totals

### Understanding the Output

#### Monthly Projections Table

Each row represents one month and includes:

**P&L Section:**
- Revenue: Total revenue for the month
- Cost of Revenue: Direct costs tied to revenue
- Gross Profit: Revenue - Cost of Revenue
- Operating Expenses: Staff and overhead costs
- CAPEX: Capital expenditures made this month
- Net Income: Gross Profit - Operating Expenses

**Cash Flow Section:**
- Cash Receipts: Actual cash received (delayed by receipt delay setting)
- Cash Payments: Actual cash paid out (delayed by payment settings)
- Net Cash Flow: Receipts - Payments
- Cash Balance: Running cash balance

**Cumulative Section:**
- Cumulative Revenue: Total revenue to date
- Cumulative Cost: Total costs to date
- Cumulative Gross Profit: Total gross profit to date

#### Summary Section

Year-by-year totals for:
- Total Revenue (Y1, Y2, Y3)
- Total Gross Profit (Y1, Y2, Y3)
- Total Net Income (Y1, Y2, Y3)

### Example Use Cases

#### 1. SaaS Startup Growth Model

```
Revenue Assumptions:
- Basic Plan: $10/month, 100 new customers/month
- Pro Plan: $50/month, 20 new customers/month
- Annual price increase: 5%

Cost Assumptions:
- Hosting: $0.50 per customer (follows customer count)
- API Costs: 10% of revenue
- Payment Processing: 3% of revenue

Staff:
- 2 Founders: $5,000/month each, Year 1
- 3 Engineers: $8,000/month each, start Month 6
- 1 Sales: $6,000/month, start Month 9
- Annual increases: 10%

CAPEX:
- Office Setup: $10,000, Month 1
- Development Equipment: $15,000, Month 1
```

#### 2. Manufacturing Expansion

```
Revenue Assumptions:
- Product Line A: $1,000/unit, 50 units/month
- Product Line B: $2,500/unit, 20 units/month
- Annual price increase: 3%

Cost Assumptions:
- Raw Materials: 40% of revenue
- Manufacturing Labor: $20,000/month fixed
- Packaging: 5% of revenue

Staff:
- Management: 3 positions, $80,000-$120,000/year
- Production Workers: 10 positions, $40,000/year
- Sales Team: 2 positions, start Year 2

CAPEX:
- Manufacturing Equipment: $500,000, Month 1
- Facility Improvements: $200,000, Month 3
- Additional Equipment: $300,000, Year 2
```

## Module Structure

```
financial_projections/
├── __init__.py
├── hooks.py
├── financial_projections/
│   ├── __init__.py
│   └── doctype/
│       ├── financial_projection/
│       │   ├── financial_projection.json
│       │   └── financial_projection.py
│       ├── financial_projection_revenue_line/
│       │   ├── financial_projection_revenue_line.json
│       │   └── financial_projection_revenue_line.py
│       ├── financial_projection_cost_line/
│       │   ├── financial_projection_cost_line.json
│       │   └── financial_projection_cost_line.py
│       ├── financial_projection_staff_line/
│       │   ├── financial_projection_staff_line.json
│       │   └── financial_projection_staff_line.py
│       ├── financial_projection_capex_line/
│       │   ├── financial_projection_capex_line.json
│       │   └── financial_projection_capex_line.py
│       └── financial_projection_monthly_data/
│           ├── financial_projection_monthly_data.json
│           └── financial_projection_monthly_data.py
```

## Technical Details

### Calculation Logic

The module uses server-side Python calculations that run automatically when:
- Document is saved
- Any assumption field is changed
- Manual recalculation is triggered

**Key Algorithms:**

1. **Revenue Calculation:**
   - Tracks carried-forward instances month-to-month
   - Applies monthly new sales
   - Calculates price with annual increases
   - Handles recurring vs one-time revenue types

2. **Cost Calculation:**
   - Links costs to revenue types for instance-based costs
   - Applies percentage calculations to corresponding revenue
   - Maintains fixed monthly costs

3. **Cash Flow:**
   - Implements payment delay logic
   - Tracks cash receipts separately from revenue recognition
   - Tracks cash payments separately from expense recognition
   - Maintains running cash balance

### Data Model

**Financial Projection (Parent Document)**
- Basic information and settings
- Cash flow parameters
- Summary calculations

**Revenue Line (Child Table)**
- Revenue type and pricing
- Volume/growth assumptions
- Calculation method

**Cost Line (Child Table)**
- Cost type and amount
- Calculation method (per instance, fixed, percentage)
- Link to revenue type

**Staff Line (Child Table)**
- Position details
- Compensation structure
- Start timing and growth

**CAPEX Line (Child Table)**
- Asset information
- Purchase timing and amount
- Depreciation details

**Monthly Data (Child Table - Calculated)**
- Month-by-month P&L
- Cash flow details
- Cumulative totals

## Extending the Module

### Adding Custom Fields

You can extend the doctypes through Frappe's customization:

1. Go to: Setup > Customize Form
2. Select "Financial Projection" or any child table
3. Add custom fields as needed
4. Update calculation logic in `financial_projection.py` if needed

### Custom Reports

Create custom reports using Frappe's report builder:

1. Go to: Build > Report
2. Select "Financial Projection Monthly Data" as the base
3. Add filters and columns as needed
4. Save and share

### API Integration

The module provides standard Frappe API endpoints:

```python
# Get projection
projection = frappe.get_doc("Financial Projection", "FY2025 Budget")

# Access monthly data
for month in projection.monthly_projections:
    print(f"Month {month.month_number}: Revenue = {month.revenue}")

# Create new projection programmatically
new_projection = frappe.get_doc({
    "doctype": "Financial Projection",
    "projection_name": "New Projection",
    "start_date": "2025-01-01",
    "cash_on_hand_start": 50000,
    "revenue_assumptions": [
        {
            "revenue_type": "Product Sales",
            "price_per_unit": 100,
            "monthly_new_sales": 50,
            "calculation_type": "Recurring"
        }
    ]
})
new_projection.insert()
```

## Limitations & Future Enhancements

### Current Limitations

1. Fixed 3-year projection period (easily configurable)
2. Simplified depreciation (straight-line only)
3. Cash flow delays use simplified logic
4. No automatic import from existing ERPNext data

### Planned Enhancements

1. **Dashboard & Visualizations**
   - Interactive charts for P&L, cash flow, and growth
   - KPI cards for key metrics
   - Scenario comparison views

2. **Advanced Features**
   - Multiple scenario modeling (best/base/worst case)
   - Actual vs. budget tracking
   - Automatic import from Sales Orders, Purchase Orders
   - Integration with ERPNext Budget module

3. **Export & Reporting**
   - Excel export with formulas intact
   - PDF reports with charts
   - Email scheduling

4. **Collaboration**
   - Comments and notes on assumptions
   - Version control for projections
   - Approval workflows

## Support & Contribution

### Getting Help

- Documentation: See this README
- Issues: Submit via GitHub Issues
- Community: Frappe Forum

### Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

### License

MIT License - See LICENSE file for details

## Credits

Developed by ES Australia for the Frappe/ERPNext community.

Based on financial projection spreadsheet templates commonly used in startup and SME financial planning.

## Changelog

### Version 0.0.1 (Initial Release)
- Basic financial projection functionality
- Revenue, cost, staff, and CAPEX modeling
- Monthly P&L and cash flow projections
- Year-by-year summary calculations
- Configurable payment delays
