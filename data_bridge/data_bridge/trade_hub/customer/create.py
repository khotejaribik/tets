import frappe
from frappe import _

from data_bridge.data_bridge.authentication.users import user_authentication
from data_bridge.data_bridge.trade_hub.utils.create import document

doctype = "Partner Customer Profile"

@frappe.whitelist()
def profile():
    
	customer, email_id, mobile_no = user_authentication()
	
	requested_data = {
		**frappe.request.form.to_dict(),
	}
	
	# Check if 'image' is present in uploaded files
	if 'image' in frappe.request.files:
		requested_data['image'] = frappe.request.files['image']

	result = document(doctype, requested_data, customer)

	response = {
		"name": result
	}

	frappe.response['data'] = response
	
