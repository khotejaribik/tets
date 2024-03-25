import frappe
import json

from frappe import _
from data_bridge.data_bridge.authentication.users import user_authentication
from data_bridge.data_bridge.validate.fields import validate_on_create_feedback
	

DOCTYPE = "Delivery Note Feedback"

def get_requested_name(customer):
	requested_name = frappe.request.args.get("name")
	
	if not requested_name:
		frappe.throw(_("Delivery Note missing."), frappe.ValidationError)

	filters = {"name": requested_name, "customer": customer}
	
	delivery_note_exists = frappe.db.exists("Delivery Note", filters)
	
	if not delivery_note_exists:
		frappe.throw(_("Delivery Note not found: ") + requested_name, frappe.DoesNotExistError)

	return requested_name


def process_feedback(requested_name, feedback_data, customer):
	
	validate_on_create_feedback(feedback_data)

	check_feedback_exists = frappe.db.exists(DOCTYPE, { "name": requested_name, "company_name": customer})
	
	if check_feedback_exists:
		
		feedback = frappe.get_doc(DOCTYPE, check_feedback_exists)
	
		feedback.update(feedback_data)
		
		save_feedback = feedback.save(ignore_permissions=True)
	
	else:
		feedback_data = {
			"doctype": DOCTYPE,
			"delivery_note": requested_name,
			"company_name": customer,
			**feedback_data
		}
	
		feedback = frappe.get_doc(feedback_data)
		save_feedback = feedback.insert(ignore_permissions=True)
  

	if not save_feedback:
		frappe.log_error("Failed to save feedback")
		frappe.throw(_("Error while saving feedback. Please try again later."), frappe.ValidationError)

	feedback_name = save_feedback.name
	return feedback_name
		

@frappe.whitelist()
def feedback():
	try:
		# Perform user authentication
		customer, email_id, mobile_no = user_authentication()
		
		company_name = customer.get("name")
  
		#Check delivery note exists or not
		requested_name = get_requested_name(company_name)
  
		# Attempt to parse the JSON data
		feedback_data = json.loads(frappe.request.data)

		# If user authentication is successful, proceed with further processing		
		feedback_name = process_feedback(requested_name, feedback_data, company_name)

		response = {
			"delivery_note": feedback_name
		}

		frappe.response['data'] = response

	except json.JSONDecodeError:
		# Handle JSON decoding error
		frappe.throw(_("Invalid JSON data. Failed to decode data."), frappe.ValidationError)