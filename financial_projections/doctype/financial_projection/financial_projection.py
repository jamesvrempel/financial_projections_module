# Copyright (c) 2024, ES Australia and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, add_months, getdate, get_first_day, get_last_day
from datetime import datetime
from dateutil.relativedelta import relativedelta

class FinancialProjection(Document):
	def validate(self):
		"""Validate the document before saving"""
		self.validate_delays()
		
	def before_save(self):
		"""Calculate projections before saving"""
		self.calculate_projections()
		
	def validate_delays(self):
		"""Validate delay parameters"""
		if self.opex_delay and (self.opex_delay < 0 or self.opex_delay > 6):
			frappe.throw("OPEX Delay must be between 0 and 6 months")
		if self.capex_delay and (self.capex_delay < 0 or self.capex_delay > 6):
			frappe.throw("CAPEX Delay must be between 0 and 6 months")
			
	def calculate_projections(self):
		"""Main calculation engine for financial projections"""
		# Clear existing projections
		self.monthly_projections = []
		
		# Calculate number of months
		total_months = (self.projection_years or 3) * 12
		
		# Initialize tracking variables
		cumulative_revenue = 0
		cumulative_cost = 0
		cumulative_gross_profit = 0
		cumulative_opex = 0
		cumulative_net_income = 0
		cash_balance = flt(self.cash_on_hand_start)
		
		# Track carried forward instances/volumes
		carried_instances = {}
		
		# Process each month
		for month_num in range(1, total_months + 1):
			month_date = add_months(self.start_date, month_num - 1)
			year_num = ((month_num - 1) // 12) + 1
			month_in_year = ((month_num - 1) % 12) + 1
			
			# Calculate revenue for this month
			revenue = self.calculate_monthly_revenue(month_num, year_num, month_in_year, carried_instances)
			
			# Calculate cost of revenue
			cost_of_revenue = self.calculate_monthly_cost(month_num, year_num, month_in_year, carried_instances)
			
			# Calculate gross profit
			gross_profit = revenue - cost_of_revenue
			
			# Calculate operating expenses
			opex = self.calculate_monthly_opex(month_num, year_num, month_in_year)
			
			# Calculate CAPEX
			capex = self.calculate_monthly_capex(month_num, year_num, month_in_year)
			
			# Calculate net income (EBITDA for simplicity)
			net_income = gross_profit - opex
			
			# Calculate cash flow
			cash_receipts = self.calculate_cash_receipts(month_num, revenue)
			cash_payments_cor = self.calculate_cash_payments_cor(month_num, cost_of_revenue)
			cash_payments_opex = self.calculate_cash_payments_opex(month_num, opex)
			cash_payments_capex = self.calculate_cash_payments_capex(month_num, capex)
			
			net_cash_flow = cash_receipts - cash_payments_cor - cash_payments_opex - cash_payments_capex
			cash_balance += net_cash_flow
			
			# Update cumulative totals
			cumulative_revenue += revenue
			cumulative_cost += cost_of_revenue
			cumulative_gross_profit += gross_profit
			cumulative_opex += opex
			cumulative_net_income += net_income
			
			# Create monthly projection row
			monthly_row = self.append('monthly_projections', {})
			monthly_row.month_number = month_num
			monthly_row.month_date = month_date
			monthly_row.year_number = year_num
			monthly_row.revenue = revenue
			monthly_row.cost_of_revenue = cost_of_revenue
			monthly_row.gross_profit = gross_profit
			monthly_row.operating_expenses = opex
			monthly_row.capex = capex
			monthly_row.net_income = net_income
			monthly_row.cash_receipts = cash_receipts
			monthly_row.cash_payments = cash_payments_cor + cash_payments_opex + cash_payments_capex
			monthly_row.net_cash_flow = net_cash_flow
			monthly_row.cash_balance = cash_balance
			monthly_row.cumulative_revenue = cumulative_revenue
			monthly_row.cumulative_cost = cumulative_cost
			monthly_row.cumulative_gross_profit = cumulative_gross_profit
			
		# Update summary fields
		self.update_summary_fields()
		
	def calculate_monthly_revenue(self, month_num, year_num, month_in_year, carried_instances):
		"""Calculate revenue for a specific month"""
		total_revenue = 0
		
		for revenue_line in self.revenue_assumptions:
			if not revenue_line.revenue_type:
				continue
				
			# Calculate instances/volume for this month
			instances = self.get_monthly_instances(revenue_line, month_num, year_num, carried_instances)
			
			# Calculate price (with annual increases)
			price = self.get_monthly_price(revenue_line, year_num)
			
			# Calculate revenue
			if revenue_line.calculation_type == "Recurring":
				# Monthly recurring revenue
				monthly_revenue = instances * price
			elif revenue_line.calculation_type == "One-Time":
				# One-time project revenue (spread over implementation months if specified)
				if revenue_line.implementation_months and revenue_line.implementation_months > 0:
					if month_in_year <= revenue_line.implementation_months:
						monthly_revenue = (instances * price) / revenue_line.implementation_months
					else:
						monthly_revenue = 0
				else:
					monthly_revenue = instances * price if month_in_year == 1 else 0
			else:
				monthly_revenue = 0
				
			total_revenue += monthly_revenue
			
		return total_revenue
		
	def calculate_monthly_cost(self, month_num, year_num, month_in_year, carried_instances):
		"""Calculate cost of revenue for a specific month"""
		total_cost = 0
		
		for cost_line in self.cost_assumptions:
			if not cost_line.cost_type:
				continue
				
			# Get instances from revenue assumptions
			instances = self.get_cost_instances(cost_line, month_num, year_num, carried_instances)
			
			# Calculate cost based on type
			if cost_line.calculation_type == "Per Instance":
				monthly_cost = instances * flt(cost_line.cost_per_unit)
			elif cost_line.calculation_type == "Fixed Monthly":
				monthly_cost = flt(cost_line.cost_per_unit)
			elif cost_line.calculation_type == "Percentage of Revenue":
				# Calculate as percentage of related revenue
				revenue = self.get_related_revenue(month_num, cost_line.related_revenue_type)
				monthly_cost = revenue * (flt(cost_line.cost_percentage) / 100)
			else:
				monthly_cost = 0
				
			total_cost += monthly_cost
			
		return total_cost
		
	def calculate_monthly_opex(self, month_num, year_num, month_in_year):
		"""Calculate operating expenses for a specific month"""
		total_opex = 0
		
		for staff_line in self.staff_assumptions:
			if not staff_line.position_title:
				continue
				
			# Check if position is active in this month
			start_month = staff_line.start_month or 1
			
			if month_num >= start_month:
				# Calculate monthly cost with annual increases
				base_salary = flt(staff_line.monthly_salary)
				benefits = flt(staff_line.monthly_benefits)
				vehicle = flt(staff_line.vehicle_allowance)
				
				# Apply annual increase
				if staff_line.annual_increase and year_num > 1:
					increase_factor = (1 + flt(staff_line.annual_increase) / 100) ** (year_num - 1)
					base_salary *= increase_factor
					
				monthly_cost = base_salary + benefits + vehicle
				total_opex += monthly_cost
				
		return total_opex
		
	def calculate_monthly_capex(self, month_num, year_num, month_in_year):
		"""Calculate capital expenditures for a specific month"""
		total_capex = 0
		
		for capex_line in self.capex_assumptions:
			if not capex_line.asset_name:
				continue
				
			# Check if CAPEX occurs in this month
			purchase_month = capex_line.purchase_month or 1
			purchase_year = capex_line.purchase_year or 1
			
			target_month = (purchase_year - 1) * 12 + purchase_month
			
			if month_num == target_month:
				total_capex += flt(capex_line.cost)
				
		return total_capex
		
	def get_monthly_instances(self, revenue_line, month_num, year_num, carried_instances):
		"""Calculate instances/volume for a revenue line"""
		key = revenue_line.revenue_type
		
		# Get new sales for this month
		new_sales = flt(revenue_line.monthly_new_sales)
		
		# Get or initialize carried instances
		if key not in carried_instances:
			carried_instances[key] = 0
			
		# Add new sales to carried instances
		carried_instances[key] += new_sales
		
		return carried_instances[key]
		
	def get_cost_instances(self, cost_line, month_num, year_num, carried_instances):
		"""Get instances for cost calculation based on related revenue"""
		if cost_line.related_revenue_type:
			return carried_instances.get(cost_line.related_revenue_type, 0)
		return 0
		
	def get_monthly_price(self, revenue_line, year_num):
		"""Calculate price with annual increases"""
		base_price = flt(revenue_line.price_per_unit)
		
		if revenue_line.annual_price_increase and year_num > 1:
			increase_factor = (1 + flt(revenue_line.annual_price_increase) / 100) ** (year_num - 1)
			return base_price * increase_factor
			
		return base_price
		
	def get_related_revenue(self, month_num, revenue_type):
		"""Get revenue for a specific type in a specific month"""
		if self.monthly_projections and len(self.monthly_projections) >= month_num:
			# This is a simplified version - in full implementation would track by type
			return flt(self.monthly_projections[month_num - 1].revenue) if month_num <= len(self.monthly_projections) else 0
		return 0
		
	def calculate_cash_receipts(self, month_num, revenue):
		"""Calculate cash receipts with delay"""
		delay = flt(self.cash_receipt_delay)
		
		if delay == 0:
			return revenue
			
		# In a full implementation, would look back at revenue from (month_num - delay)
		# For prototype, simplified to current month
		return revenue if month_num > delay else 0
		
	def calculate_cash_payments_cor(self, month_num, cost):
		"""Calculate cash payments for cost of revenue with delay"""
		delay = flt(self.cost_of_revenue_delay)
		
		if delay == 0:
			return cost
			
		return cost if month_num > delay else 0
		
	def calculate_cash_payments_opex(self, month_num, opex):
		"""Calculate cash payments for OPEX with delay"""
		delay = flt(self.opex_delay)
		
		if delay == 0:
			return opex
			
		return opex if month_num > delay else 0
		
	def calculate_cash_payments_capex(self, month_num, capex):
		"""Calculate cash payments for CAPEX with delay"""
		delay = flt(self.capex_delay)
		
		if delay == 0:
			return capex
			
		return capex if month_num > delay else 0
		
	def update_summary_fields(self):
		"""Update summary totals by year"""
		if not self.monthly_projections:
			return
			
		# Initialize year totals
		year_revenue = {1: 0, 2: 0, 3: 0}
		year_gross_profit = {1: 0, 2: 0, 3: 0}
		year_net_income = {1: 0, 2: 0, 3: 0}
		
		# Sum up by year
		for row in self.monthly_projections:
			year = row.year_number
			if year in year_revenue:
				year_revenue[year] += flt(row.revenue)
				year_gross_profit[year] += flt(row.gross_profit)
				year_net_income[year] += flt(row.net_income)
				
		# Update fields
		self.total_revenue_y1 = year_revenue.get(1, 0)
		self.total_revenue_y2 = year_revenue.get(2, 0)
		self.total_revenue_y3 = year_revenue.get(3, 0)
		
		self.total_gross_profit_y1 = year_gross_profit.get(1, 0)
		self.total_gross_profit_y2 = year_gross_profit.get(2, 0)
		self.total_gross_profit_y3 = year_gross_profit.get(3, 0)
		
		self.total_net_income_y1 = year_net_income.get(1, 0)
		self.total_net_income_y2 = year_net_income.get(2, 0)
		self.total_net_income_y3 = year_net_income.get(3, 0)
