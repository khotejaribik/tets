import frappe
import json

from frappe import _
from data_bridge.data_bridge.authentication.users import user_authentication
from data_bridge.data_bridge.utils.admin_notification import send_notification
from data_bridge.data_bridge.validate.fields import validate_on_create_quotation, validate_item
from data_bridge.data_bridge.validate.otp import validate_otp
from data_bridge.data_bridge.utils.incoming_sms import get_incoming_sms_setting


def process_quotation(quotation_data, customer, email_id, mobile_no):

	validate_otp(mobile_no, quotation_data['otp'])
	
	validate_on_create_quotation(quotation_data)
  
	for item in quotation_data.get("items", []):
		item_code = validate_item(item)
		
		# Add item_code to the item
		item["item_code"] = item_code

		# Remove the "name" field from the item
		item.pop("name", None)

	contact_person = customer.get("customer_primary_contact")

	quotation_data.pop("otp")

	quotation_data = {
		"doctype": "Quotation",
		"party_name": customer.get("name"),
		"contact_person": contact_person,
		"contact_email": email_id,
		"order_type": "Shopping Cart",
		**quotation_data
	}

	quotation = frappe.get_doc(quotation_data)
	
	save_quotation = quotation.insert(ignore_permissions=True)

	if not save_quotation:
		frappe.log_error("Failed to save quotation")
		frappe.throw(_("Error while saving quotation. Please try again later."), frappe.ValidationError)
	
	quotation_name = save_quotation.name
	
	incoming_sms = get_incoming_sms_setting()
	admin_number = incoming_sms.get("admin_number")
	partner_quotation_message = incoming_sms.get("partner_quotation_message")

	# send_notification(contact_person, mobile_no, quotation_name, admin_number, partner_quotation_message)

	return quotation_name


@frappe.whitelist()
def quotation():
	try:
		# Perform user authentication
		customer, email_id, mobile_no = user_authentication()

		# Attempt to parse the JSON data
		quotation_data = json.loads(frappe.request.data)

		# If user authentication is successful, proceed with further processing		
		quotation_name = process_quotation(quotation_data, customer, email_id, mobile_no)

		response = {
			"quotation_name": quotation_name
		}

		frappe.response['data'] = response

	except json.JSONDecodeError:
		# Handle JSON decoding error
		frappe.throw(_("Invalid JSON data. Failed to decode quotation data."), frappe.ValidationError)