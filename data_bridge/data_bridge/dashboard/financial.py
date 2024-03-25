import frappe

from frappe import _
from data_bridge.data_bridge.authentication.users import user_authentication


def get_current_fiscal_year():
    # Fetch the current date
    current_date = frappe.utils.nowdate()

    # Get the fiscal year based on the current date
    fiscal_year = frappe.db.sql("""
        SELECT name
        FROM `tabFiscal Year`
        WHERE %(current_date)s BETWEEN year_start_date AND year_end_date
    """, {"current_date": current_date}, as_dict=True)

    if fiscal_year:
        return fiscal_year[0]["name"]
    else:
        return None


def get_requested_year():
	requested_year = frappe.form_dict.year

	if not requested_year:
		return get_current_fiscal_year()
	
	return requested_year
	

def get_fiscal_year(requested_year):
	
	get_fiscal = frappe.db.get_value("Fiscal Year", {"name": requested_year}, ['year_start_date', 'year_end_date'], as_dict = True)
	
	if not get_fiscal:
		frappe.throw(_("Fiscal year does not exists."), frappe.DoesNotExistError)

	return get_fiscal


def get_return_invoices(customer, fiscal_year_start, fiscal_year_end):
	doctype = "Sales Invoice"
	return_invoices = frappe.db.get_all(
			doctype,
			filters={
				"is_return": 1,
				"docstatus": 1,
				"posting_date": ["between", [fiscal_year_start, fiscal_year_end]],
				"customer": customer,
			},
			fields = ['name']
		)
	
	return [invoice["name"] for invoice in return_invoices]
		
  	
def get_customer_balance_for_fiscal_year(customer, fiscal_year_start, fiscal_year_end):
	filters = {
		"party_type": "Customer",
		"party": customer,
		"posting_date": (">=", fiscal_year_start),
		"posting_date": ("<=", fiscal_year_end),
		"docstatus": ["<", 2],
		"is_cancelled": 0,
	}

	gl_entries = frappe.get_all("GL Entry", filters=filters, fields=["debit", "credit", "posting_date", "party", "is_opening", "voucher_no"])

	opening_balance = 0
	closing_balance = 0
	invoiced_amount = 0
	return_amount = 0
	paid_amount = 0
	
	return_invoices = get_return_invoices(customer, fiscal_year_start, fiscal_year_end)
	
	for entry in gl_entries:
		amount = entry.debit - entry.credit
		
		closing_balance = int(closing_balance + amount)
		
		if entry.posting_date < fiscal_year_start or entry.is_opening == "Yes":
			opening_balance = int(opening_balance + amount)
		else:
			if amount > 0:
				invoiced_amount = int(invoiced_amount + amount)
			elif entry.voucher_no in return_invoices:
				return_amount = int(return_amount - amount)
			else:
				paid_amount = int(paid_amount - amount)

	return {
		'opening_balance': opening_balance,
		'invoiced_amount': invoiced_amount,
		'paid_amount': paid_amount,
		'return_amount': return_amount,
		'closing_balance': closing_balance,
	}


def get_sales_order(customer_name, fiscal_year_start, fiscal_year_end):
	
	sales_orders = frappe.db.get_all(
			'Sales Order',
			filters={
				'customer': customer_name,
				'status': ['not in', ['Draft', 'Cancelled', 'On Hold']],
				'transaction_date': ['between', [fiscal_year_start, fiscal_year_end]],
				'docstatus' : 1
			},
			fields=['transaction_date', 'grand_total', 'name', 'conversion_rate'],
			order_by='transaction_date desc'
		)
	
	return sales_orders


def get_delivery_note(customer_name, fiscal_year_start, fiscal_year_end):
	
	delivery_notes = frappe.db.get_all(
			'Delivery Note',
			filters={
				'customer': customer_name,
				'status': ['not in', ['Draft', 'Cancelled', 'Return Issued']],
				'posting_date': ['between', [fiscal_year_start, fiscal_year_end]],
				'docstatus' : 1,
				'is_return': 0,
			},
			fields=['posting_date', 'grand_total', 'name'],
			order_by='posting_date desc'
		)
	
	return delivery_notes


def get_top_purchased_items (customer_name, fiscal_year_start, fiscal_year_end):
	
	delivery_notes = get_delivery_note(customer_name, fiscal_year_start, fiscal_year_end)
  
	delivery_notes_name = [so['name'] for so in delivery_notes]
 
	top_items = frappe.db.get_all(
			'Delivery Note Item',
			filters={
				'parent': ['in', delivery_notes_name]
			},
			fields=['image', 'item_code', 'sum(qty) as qty'],
			group_by='item_code',
			order_by='qty desc',
			limit=5
		)

	return top_items
 

def get_purchase_invoice_donut(customer_name, fiscal_year_start, fiscal_year_end):

	sales_orders = get_sales_order(customer_name, fiscal_year_start, fiscal_year_end)

	# Extract Sales Order names and corresponding conversion rates
	sales_order_data = {so['name']: so['conversion_rate'] for so in sales_orders}

	# Fetch Sales Order Items with calculated fields
	sales_items = frappe.db.get_all(
		'Sales Order Item',
		filters={'parent': ['in', list(sales_order_data.keys())]},
		fields=[
			'parent',  # Sales Order name
			'billed_amt',
			'base_amount'
		]
	)

	# Calculate billed_amount and pending_amount for each Sales Order Item
	total_billed_amount = 0
	total_pending_amount = 0

	for item in sales_items:
		conversion_rate = sales_order_data.get(item['parent'], 1)

		billed_amount = int(item['billed_amt'] * conversion_rate)
		pending_amount = int(item['base_amount'] - billed_amount)

		total_billed_amount += billed_amount
		total_pending_amount += pending_amount

	# Calculate total amount
	total_amount = total_billed_amount + total_pending_amount
 
	# Calculate percentages only if total_amount is not zero
	if total_amount != 0:
		percentage_billed = round((total_billed_amount / total_amount) * 100, 1)
		percentage_pending = round((total_pending_amount / total_amount) * 100, 1)
	else:
		# Set percentages to zero or any default value based on your requirements
		percentage_billed = 0
		percentage_pending = 0

	# Prepare detailed response
	response = {
		"billed_amount": {
			"amount": total_billed_amount,
			"percentage": percentage_billed
		},
		"amount_to_bill": {
			"amount": total_pending_amount,
			"percentage": percentage_pending
		}
	}

	return response

def get_monthly_purchase_order(customer_name, fiscal_year_start, fiscal_year_end):
	start_month = fiscal_year_start.month
	end_month = fiscal_year_end.month
	monthly_totals_order = [0] * 12

	sales_orders = get_sales_order (customer_name, fiscal_year_start, fiscal_year_end)

	for order in sales_orders:
		order_month = order['transaction_date'].month
		if start_month <= order_month <= end_month:
			month_index = (order_month - start_month) % 12
			monthly_totals_order[month_index] += order['grand_total']

	monthly_totals_order = [int(total) for total in monthly_totals_order]

	return monthly_totals_order


def get_monthly_purchase_invoice(customer_name, fiscal_year_start, fiscal_year_end):
	start_month = fiscal_year_start.month
	end_month = fiscal_year_end.month

	# Create a list to store the monthly totals
	monthly_totals_invoice = [0] * 12

	# Get the sales invoices for the given year
	sales_invoices = frappe.get_all('Sales Invoice',
						filters={
							'customer': customer_name,
							"status": ['not in', ['Draft', 'Cancelled']],
							"posting_date": ["between", [fiscal_year_start, fiscal_year_end]],
	   						"docstatus" : 1,
						},
						fields=['posting_date', 'grand_total'],
						order_by='posting_date desc'
						)
 
	# Loop through the sales invoices and add the grand total to the appropriate month
	for invoice in sales_invoices:
		invoice_month = invoice['posting_date'].month
		if start_month <= invoice_month <= end_month:
			month_index = (invoice_month - start_month) % 12  # Calculate the month index in the range 0-11
			monthly_totals_invoice[month_index] += invoice['grand_total']

	monthly_totals_invoice = [int(total) for total in monthly_totals_invoice]

	return monthly_totals_invoice


@frappe.whitelist()	
def read():
	
	customer, email_id, mobile_no = user_authentication()
	
	customer_name = customer.get("name")
	
	requested_year = get_requested_year()
	
	fiscal_year = get_fiscal_year(requested_year)
	
	year_start_date = fiscal_year.get("year_start_date")
	year_end_date = fiscal_year.get("year_end_date")
		
	customer_financial_data = get_customer_balance_for_fiscal_year(customer_name, year_start_date, year_end_date)
	top_purchased_items = get_top_purchased_items (customer_name, year_start_date, year_end_date)
	purchase_invoice_donut = get_purchase_invoice_donut(customer_name, year_start_date, year_end_date)
	purchase_order_chart = get_monthly_purchase_order(customer_name, year_start_date, year_end_date)
	purchase_invoice_chart = get_monthly_purchase_invoice(customer_name, year_start_date, year_end_date)

	response = {
		"financial_status": customer_financial_data,
		"top_purchased_items": top_purchased_items,
		"purchase_invoice_donut": purchase_invoice_donut,
  		"purchase_order_chart" : purchase_order_chart,
		"purchase_invoice_chart" : purchase_invoice_chart,
		}
 
	frappe.response['data'] = response

