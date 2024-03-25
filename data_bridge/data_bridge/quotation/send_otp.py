import frappe

from frappe import _
from data_bridge.data_bridge.authentication.users import user_authentication
from data_bridge.data_bridge.authentication.otp_config import get_sms_settings, get_otp_settings, generate_otp_code, config_process_otp_code, get_company_name


def process_otp_code(settings, mobile_no, otp_code, otp_expires_in_minutes, email_id):
	try:
		company = get_company_name()
		text = f"Your OTP is {otp_code} for quotation. " + "-" + company

		response = config_process_otp_code(settings, text, mobile_no)
		response_message =  response.get('response_message')
		sms_shootid =  response.get('sms_shootid')
		
		if response_message == "success":
			sent_on = frappe.utils.now_datetime()
			expires_on = frappe.utils.add_to_date(sent_on, minutes=otp_expires_in_minutes)
			diff = expires_on - sent_on
			minutes = int(diff.total_seconds() / 60)

			response = save_login_otp_log(mobile_no, otp_code, sms_shootid, sent_on, expires_on, minutes)
   
			frappe.sendmail(
				recipients= email_id,
				message= text,
				subject= "Your verification code for quotation",
				now = True
			)

			return response
			
		else:
			raise frappe.AuthenticationError

	except Exception as e:
		frappe.log_error(f"An error occurred during SMS sending: {str(e)}")
		frappe.throw(_("An error occurred while sending the SMS. Please try again."), frappe.AuthenticationError)


def save_login_otp_log(mobile_no, otp_code, sms_shootid, sent_on, expires_on, minutes):

	check_otp_log = frappe.db.exists("Quotation OTP Log", {"requested_number": mobile_no})

	if check_otp_log:
		login_log = frappe.get_doc("Quotation OTP Log", check_otp_log)
	else:
		login_log = frappe.get_doc({
			'doctype': 'Quotation OTP Log',
			'requested_number': mobile_no,
		})

	login_log.otp_code = otp_code
	login_log.sms_shootid = sms_shootid
	login_log.sent_on = sent_on
	login_log.expires_on = expires_on
	login_log.time = minutes
	login_log.status = "Active"
	login_log.user_type = "Partner"
	
	save_login = login_log.save(ignore_permissions=True)
	
	if not save_login:
		frappe.log_error("Failed to save otp")
		frappe.throw(_("An error occurred. Please try again."), frappe.ValidationError)
		
	response = {
		"expires_on": login_log.expires_on,
		"status": login_log.status
	}
	
	return response


@frappe.whitelist()
def send_otp():

	customer, email_id, mobile_no = user_authentication()

	settings = get_sms_settings()

	otp_length, otp_expires_in_minutes = get_otp_settings()

	otp_code = generate_otp_code(otp_length)

	send_otp_code = process_otp_code(settings, mobile_no, otp_code, otp_expires_in_minutes, email_id)

	frappe.response['data'] = send_otp_code

