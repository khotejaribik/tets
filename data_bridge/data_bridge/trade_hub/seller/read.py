import frappe
from frappe import _

from data_bridge.data_bridge.authentication.users import user_authentication
from data_bridge.data_bridge.trade_hub.utils.read import trade_data

DOCTYPE = "Partner Seller Profile"

@frappe.whitelist()
def profile():
	customer, email_id, mobile_no = user_authentication()
	customer_name = customer.get("name")

	filters = {"my_company_name": customer_name}
	fields = ["name", "image", "company_name", "designation", 'seller_name', 'tax_id', 'address', 'contact_number', 'email', 'notes']
	order_by = 'modified desc'
 
	# Call trade_data with named parameters for clarity
	result = trade_data(DOCTYPE, filters, fields, order_by)

	# Ensure that the trade_data function returns the expected structure
	data = result.get("data", [])
	count = result.get("count", 0)

	response = {
		'list': data,
		'count': count,
	}

	frappe.response['data'] = response