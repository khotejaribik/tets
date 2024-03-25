import frappe
import json
from frappe import _

from data_bridge.data_bridge.authentication.users import user_authentication
from data_bridge.data_bridge.trade_hub.sales.function import process_quotation


def get_requested_quotation(customer):
	
	requested_quotation = frappe.request.args.get("name")
	
	if not requested_quotation:
		frappe.throw(_("Quotation name missing."), frappe.ValidationError)
		
	check_quotation_exists = frappe.db.exists("Partner Quotation", {"name": requested_quotation, "my_company_name": customer.get("name")})
	
	if not check_quotation_exists:
		frappe.throw(_("Quotation not found: ") + requested_quotation, frappe.DoesNotExistError)
		
	return requested_quotation


def update_quotation(requested_quotation, quotation_data, customer):
    quotation_doc = frappe.get_doc("Partner Quotation", {"name": requested_quotation, "my_company_name": customer.get("name")})

    quotation_data = process_quotation (quotation_data, customer)
        
     # Save the updated document
    try:
        quotation_doc.update(quotation_data)
        quotation_doc.save(ignore_permissions=True)
        
    except Exception as e:
        frappe.log_error("Failed to update quotation: " + str(e))
        frappe.throw(_("Error while updating quotation. Please try again later."), frappe.ValidationError)

    quotation_name = quotation_doc.name
    return quotation_name



@frappe.whitelist()
def order():
    try:
        # Perform user authentication
        customer, email_id, mobile_no = user_authentication()

        requested_quotation = get_requested_quotation(customer)

        # Attempt to parse the JSON data
        quotation_data = json.loads(frappe.request.data)

        # If user authentication is successful, proceed with further processing
        quotation_name = update_quotation(requested_quotation, quotation_data, customer)

        response = {"quotation_name": quotation_name}
        frappe.response['data'] = response

    except json.JSONDecodeError:
        # Handle JSON decoding error
        frappe.throw(_("Invalid JSON data. Failed to decode quotation data."), frappe.ValidationError)
