import frappe
import json

from frappe import _
from data_bridge.data_bridge.authentication.users import user_authentication
from data_bridge.data_bridge.validate.fields import validate_on_create_warranty

def process_warranty(warranty_data, customer):
	
	validate_on_create_warranty(warranty_data)

	customer_name = customer.get("name")
	contact_person = customer.get("customer_primary_contact")

	serial_no = warranty_data.get("serial_no")
	
	item_detail =  get_serial_detail(serial_no)
 
	warranty_data = {
		"doctype": "Warranty Claim",
		"customer": customer_name,
		"customer_name": customer_name,
		"contact_person": contact_person,
		"item_code" : item_detail.get("item_code"),
		"item_name" : item_detail.get("item_name"),
		"description" : item_detail.get("description"),
  		"warranty_amc_status" : item_detail.get("maintenance_status"),
		"warranty_expiry_date" : item_detail.get("warranty_expiry_date"),
		**warranty_data
	}

	warranty = frappe.get_doc(warranty_data)
	
	save_warranty = warranty.insert(ignore_permissions=True)

	if not save_warranty:
		frappe.log_error("Failed to save warranty")
		frappe.throw(_("Error while saving warranty. Please try again later."), frappe.ValidationError)
	
	warranty_name = save_warranty.name
	
	return warranty_name


def get_serial_detail(serial_no):
	
	filters={
		'serial_no': serial_no
	}
	
	fields=['item_code', 'item_name', 'description', 'warranty_expiry_date', 'maintenance_status']

	serial_no = frappe.db.get_value("Serial No", filters, fields, as_dict=True)
 
	return serial_no


@frappe.whitelist()
def warranty():
	try:
		# Perform user authentication
		customer, email_id, mobile_no = user_authentication()

		# Attempt to parse the JSON data
		warranty_data = json.loads(frappe.request.data)
		
		# If user authentication is successful, proceed with further processing		
		warranty_name = process_warranty(warranty_data, customer)

		response = {
			"warranty_name": warranty_name
		}

		frappe.response['data'] = response

	except json.JSONDecodeError:
		# Handle JSON decoding error
		frappe.throw(_("Invalid JSON data. Failed to decode quotation data."), frappe.ValidationError)