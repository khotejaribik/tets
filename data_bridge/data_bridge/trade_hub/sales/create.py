import frappe
import json
from frappe import _

from data_bridge.data_bridge.authentication.users import user_authentication
from data_bridge.data_bridge.trade_hub.sales.function import process_quotation


def create_quotation(quotation_data, customer):
    
    quotation_data = process_quotation (quotation_data, customer)
    
    quotation = frappe.get_doc(quotation_data)
    save_quotation = quotation.insert(ignore_permissions=True)

    if not save_quotation:
        frappe.log_error("Failed to save quotation")
        frappe.throw(_("Error while saving quotation. Please try again later."), frappe.ValidationError)

    return save_quotation.name


@frappe.whitelist()
def order():
    try:
        # Perform user authentication
        customer, email_id, mobile_no = user_authentication()

        # Attempt to parse the JSON data
        quotation_data = json.loads(frappe.request.data)

        # If user authentication is successful, proceed with further processing
        quotation_name = create_quotation(quotation_data, customer)

        response = {"quotation_name": quotation_name}
        frappe.response['data'] = response

    except json.JSONDecodeError:
        # Handle JSON decoding error
        frappe.throw(_("Invalid JSON data. Failed to decode quotation data."), frappe.ValidationError)
