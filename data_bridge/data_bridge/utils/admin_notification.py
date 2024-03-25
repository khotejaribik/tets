import frappe

from frappe import _
from data_bridge.data_bridge.authentication.otp_config import get_sms_settings, config_process_otp_code


def send_notification(contact_person, mobile_no, quotation_name, admin_number, message, guest=False):
	try:
		text = f"{message}\nQuotation Number: {quotation_name}\nCompany Name: {contact_person}\nCustomer Number: {mobile_no}"
		settings = get_sms_settings()
		response = config_process_otp_code(settings, text, admin_number)
		response_message =  response.get('response_message')
		sms_shootid =  response.get('sms_shootid')
		
		if response_message == "success":
			sent_on = frappe.utils.now_datetime()

			response = save_notification(text, mobile_no, contact_person, sms_shootid, sent_on, guest)
			return response
			
		else:
			frappe.throw(_("An error occurred while sending notification to admin. Please try again."), frappe.AuthenticationError)

	except Exception as e:
		frappe.log_error(f"An error occurred during SMS sending: {str(e)}")
		frappe.throw(_("An error occurred while sending the SMS. Please try again."), frappe.AuthenticationError)


def save_notification(text, mobile_no, contact_person, sms_shootid, sent_on, guest):

	user_type = "Guest" if guest else "Partner"
	incoming_log = frappe.get_doc({
					'doctype': 'Incoming SMS Log',
					'requested_number': mobile_no,
					'message': text,
					'requested_customer': contact_person,
					'sms_shootid': sms_shootid,
					'sent_on': sent_on,
					'user_type': user_type,
					'purpose': 'Quotation',
				})
			
	save_log = incoming_log.insert(ignore_permissions=True)

	if not save_log:
		frappe.log_error("Failed to save incoming_log of guest")
		frappe.throw(_("An error occurred. Please try again."), frappe.ValidationError)   

