import frappe
import json

from frappe import _
from data_bridge.data_bridge.authentication.users import user_authentication
from data_bridge.data_bridge.validate.fields import validate_on_update_quotation, validate_item


def get_requested_quotation(customer):
	requested_quotation = frappe.request.args.get("name")

	if not requested_quotation:
		frappe.throw(_("Quotation name missing."), frappe.ValidationError)
		
	check_quotation_exists = frappe.db.exists("Quotation", {"name": requested_quotation, "party_name": customer.get("name")})
	
	if not check_quotation_exists:
		frappe.throw(_("Quotation not found: ") + requested_quotation, frappe.DoesNotExistError)
		
	return requested_quotation


def update_quotation_items(doc, quotation_data):

	# Update or add new items
	for item in quotation_data['items']:
		item_code = validate_item(item)

		item["item_code"] = item_code
		# Remove the "name" field from the item
		item.pop("name", None)

	# Save the updated document
	try:
		doc.update(quotation_data)
		doc.save(ignore_permissions=True)
		
	except Exception as e:
		frappe.log_error("Failed to update quotation: " + str(e))
		frappe.throw(_("Error while updating quotation. Please try again later."), frappe.ValidationError)

	quotation_name = doc.name
	return quotation_name


def process_quotation(requested_quotation, quotation_data, customer):
	validate_on_update_quotation(quotation_data)

	# Try to fetch the Quotation based on the provided filters
	quotation_doc = frappe.get_doc("Quotation", {"name": requested_quotation, "party_name": customer.get("name"), "status": "Draft"})

	# Call the update_quotation_items function
	response = update_quotation_items(quotation_doc, quotation_data)
	return response  # Return the response
		

@frappe.whitelist()
def quotation():
	try:
		# Perform user authentication
		customer, email_id, mobile_no = user_authentication()

		requested_quotation = get_requested_quotation(customer)
	
		# Attempt to parse the JSON data
		quotation_data = json.loads(frappe.request.data)

		# If user authentication is successful, proceed with further processing		
		quotation_name = process_quotation(requested_quotation, quotation_data, customer)

		response = {
			"quotation_name": quotation_name
		}

		frappe.response['data'] = response

	except json.JSONDecodeError:
		# Handle JSON decoding error
		frappe.throw(_("Invalid JSON data. Failed to decode quotation data."), frappe.ValidationError)