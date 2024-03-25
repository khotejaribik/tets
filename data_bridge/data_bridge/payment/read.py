import frappe

from frappe import _
from data_bridge.data_bridge.authentication.users import user_authentication


def process_payment(customer_name):
    
	start = frappe.form_dict.get('start') or 0
	page_length = frappe.form_dict.get('page_length') or 100
 
	filters = {'party_name': customer_name, 'payment_type': 'Receive', 'docstatus': 1, 'status': 'Submitted'}
	fields=['name', 'posting_date', 'mode_of_payment', 'paid_to', 'paid_amount', 'reference_no', 'reference_date', 'remarks']
	order_by = 'posting_date desc'

	payment_entry = frappe.db.get_all('Payment Entry', filters=filters, fields=fields, order_by=order_by, limit_start=start, limit_page_length=page_length)
	
	payment_count = frappe.db.count('Payment Entry', filters=filters)

	for entry in payment_entry:
		# Retrieve references using frappe.get_doc to minimize queries
		payment_doc = frappe.get_doc('Payment Entry', entry['name'])
		
		# Define the fields you want in the reference
		reference_field = ['idx', 'reference_doctype', 'reference_name', 'total_amount', 'outstanding_amount', 'allocated_amount']
		
		# Get the references with only the specified fields
		entry['references'] = [{field: payment_reference.get(field) for field in reference_field} for payment_reference in payment_doc.references]


	return {
		"list" : payment_entry,
		"count": payment_count,
	}

@frappe.whitelist()
def history():

	customer, email_id, mobile_no = user_authentication()
	customer_name = customer.get("name")

	response = process_payment(customer_name)

	frappe.response['data'] = response
