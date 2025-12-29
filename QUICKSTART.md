# Financial Projections - Quick Start Guide

## 5-Minute Setup

### Step 1: Install the Module (2 minutes)

**Option A - Using install script:**
```bash
cd /path/to/frappe-bench
./path/to/financial_projections_module/install.sh
```

**Option B - Manual installation:**
```bash
cd /path/to/frappe-bench
bench get-app /path/to/financial_projections_module
bench --site your-site-name install-app financial_projections
bench --site your-site-name migrate
bench restart
```

### Step 2: Import Sample Data (1 minute)

1. Login to your ERPNext site
2. Go to: Search bar → Type "Financial Projection"
3. Click "Menu" → "Import"
4. Upload the `sample_data.json` file
5. Click "Import"

**OR create manually:**

### Step 3: Create Your First Projection (2 minutes)

1. **New Financial Projection**
   - Name: "My First Projection"
   - Start Date: First of next month
   - Cash on Hand: 10,000

2. **Add One Revenue Line**
   - Type: "Monthly Service"
   - Price: $50/month
   - New Sales: 10 customers/month
   - Calculation: Recurring

3. **Add One Cost Line**
   - Type: "Service Cost"
   - Cost per Unit: $5
   - Related Revenue: "Monthly Service"

4. **Add One Staff Member**
   - Title: "Founder"
   - Salary: $5,000/month
   - Start Month: 1

5. **Save** → Review Monthly Projections!

## Understanding Your First Projection

After saving, scroll down to see:

### Monthly Projections Table
- **Month 1:** Revenue = $500 (10 customers × $50)
- **Cost:** $50 (10 customers × $5)
- **Gross Profit:** $450
- **OPEX:** $5,000 (founder salary)
- **Net Income:** -$4,550 (loss in month 1)
- **Cash Balance:** $5,450 remaining

### By Month 10
- **Revenue:** $5,000 (100 customers × $50)
- **Cost:** $500 (100 customers × $5)
- **Gross Profit:** $4,500
- **OPEX:** $5,000
- **Net Income:** -$500
- **Cash Balance:** Check to see if still positive!

### By Month 12
- **Revenue:** $6,000 (120 customers × $50)
- **Gross Profit:** $5,400
- **Net Income:** $400 (profitable!)

## Common Patterns

### SaaS Business
```
Revenue: Recurring monthly subscriptions
Cost: Per-customer hosting + % payment processing
Staff: Small team, growing over time
CAPEX: Minimal (mostly laptops)
```

### Product Business
```
Revenue: One-time product sales
Cost: 40-60% COGS (materials)
Staff: Production + sales team
CAPEX: Equipment, machinery
```

### Service Business
```
Revenue: Monthly retainers + project fees
Cost: Subcontractors (% of revenue)
Staff: Core team (high OPEX)
CAPEX: Minimal
```

## Key Metrics to Watch

1. **Breakeven Point:** When Net Income turns positive
2. **Cash Runway:** Months until Cash Balance reaches $0
3. **Gross Margin:** Gross Profit / Revenue (should be >60% for SaaS)
4. **Monthly Burn Rate:** Average monthly Net Income (when negative)

## Next Steps

1. **Refine Your Model**
   - Add more revenue streams
   - Include all actual costs
   - Plan staff hiring schedule
   - Add equipment purchases

2. **Create Scenarios**
   - Best Case: High growth, low costs
   - Base Case: Realistic expectations
   - Worst Case: Slow growth, high costs

3. **Compare to Actuals**
   - Export monthly data
   - Compare to actual P&L
   - Adjust assumptions
   - Update projection quarterly

4. **Share with Stakeholders**
   - Export to PDF or Excel
   - Present summary metrics
   - Discuss key assumptions
   - Get feedback and refine

## Tips & Tricks

### Modeling Seasonal Business
- Use different monthly_new_sales by creating multiple projections
- Compare different start dates

### Modeling Price Changes
- Create separate revenue lines for different price tiers
- Use annual_price_increase for inflation

### Modeling Hiring Plan
- Set start_month for each position (1-36)
- Use annual_increase for raises

### Modeling Cash Delays
- Set cash_receipt_delay to match payment terms (e.g., 1 = Net-30)
- Set cost delays to match vendor terms
- Monitor Cash Balance closely

## Troubleshooting

**Problem:** Calculations not updating
**Solution:** Click Save to trigger recalculation

**Problem:** Cash balance goes negative
**Solution:** Increase starting cash, reduce costs, or accelerate revenue

**Problem:** Need more than 3 years
**Solution:** Change projection_years field in JSON or create new projection

**Problem:** Complex depreciation schedules
**Solution:** Current version uses simplified depreciation; track separately for now

## Getting Help

- Read the full README.md
- Check calculation logic in financial_projection.py
- Post questions on Frappe Forum
- Submit issues on GitHub

## Example Output

After creating the quick start example above, your Year 1 summary will show:

```
Total Revenue Year 1:     $39,000
Gross Profit Year 1:      $35,100
Net Income Year 1:        -$24,900  (still building customer base)

Year 2 improves significantly:
Total Revenue Year 2:     $122,000
Gross Profit Year 2:      $109,800
Net Income Year 2:        +$43,800  (profitable!)

Year 3 continues growth:
Total Revenue Year 3:     $205,000
Gross Profit Year 3:      $184,500
Net Income Year 3:        +$111,900
```

This shows the typical SaaS trajectory: initial losses while building customer base, then strong profitability as recurring revenue compounds.

---

**Ready to start planning your financial future? Create your first projection now!**
