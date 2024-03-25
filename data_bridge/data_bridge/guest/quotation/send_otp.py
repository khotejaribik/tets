import frappe

from frappe import _
from data_bridge.data_bridge.authentication.otp_config import get_sms_settings, get_otp_settings, generate_otp_code, config_process_otp_code, get_company_name


def check_otp_limit(requested_number, disable_login):
    check_otp_log = frappe.db.exists("Quotation OTP Log", {"requested_number": requested_number})

    if check_otp_log:
        log_exists = frappe.get_doc("Quotation OTP Log", check_otp_log)
        last_sent_on = log_exists.sent_on
        last_count = log_exists.user_request_count

        if last_count <=0 :
            after_one_day = frappe.utils.now_datetime()
            time_diff = frappe.utils.time_diff_in_hours(after_one_day, last_sent_on)
            time_diff = int(time_diff)

            if time_diff < disable_login:
                frappe.throw(_("Your OTP Limit for today has been exceeded. If you want to request more quotation, then please contact the administrator for assistance."), frappe.ValidationError)


def process_otp_code(settings, requested_number, otp_code, otp_expires_in_minutes, otp_limit):
	try:
		company = get_company_name()
		text = f"Your OTP is {otp_code} for quotation. " + "-" + company

		response = config_process_otp_code(settings, text, requested_number)
		response_message =  response.get('response_message')
		sms_shootid =  response.get('sms_shootid')
		
		if response_message == "success":
			sent_on = frappe.utils.now_datetime()
			expires_on = frappe.utils.add_to_date(sent_on, minutes=otp_expires_in_minutes)
			diff = expires_on - sent_on
			minutes = int(diff.total_seconds() / 60)

			response = save_login_otp_log(requested_number, otp_code, sms_shootid, sent_on, expires_on, minutes, otp_limit)
			return response
			
		else:
			raise frappe.AuthenticationError

	except Exception as e:
		frappe.log_error(f"An error occurred during SMS sending: {str(e)}")
		frappe.throw(_("An error occurred while sending the SMS. Please contact the administrator for assistance."), frappe.AuthenticationError)


def save_login_otp_log(mobile_no, otp_code, sms_shootid, sent_on, expires_on, minutes, otp_limit):

	check_otp_log = frappe.db.exists("Quotation OTP Log", {"requested_number": mobile_no})

	if check_otp_log:
		login_log = frappe.get_doc("Quotation OTP Log", check_otp_log)
		login_log.user_request_count = login_log.user_request_count - 1
	else:
		login_log = frappe.get_doc({
			'doctype': 'Quotation OTP Log',
			'requested_number': mobile_no,
			'user_request_count': otp_limit
		})

	login_log.otp_code = otp_code
	login_log.sms_shootid = sms_shootid
	login_log.sent_on = sent_on
	login_log.expires_on = expires_on
	login_log.time = minutes
	login_log.status = "Active"
	login_log.user_type = "Guest"
	
	
	save_login = login_log.save(ignore_permissions=True)
	
	if not save_login:
		frappe.log_error("Failed to save otp")
		frappe.throw(_("An error occurred. Please try again."), frappe.ValidationError)
		
	response = {
		"expires_on": login_log.expires_on,
		"status": login_log.status
	}
	
	return response


@frappe.whitelist(allow_guest=True)
def send_otp():
	requested_number = frappe.form_dict.get('to')

	if not requested_number:
		frappe.throw(_("Please enter a mobile number"), frappe.ValidationError)

	settings = get_sms_settings()

	otp_length, otp_expires_in_minutes, disable_login, otp_limit = get_otp_settings(for_guest=True)
	
	check_otp_limit(requested_number, disable_login)

	otp_code = generate_otp_code(otp_length)

	send_otp_code = process_otp_code(settings, requested_number, otp_code, otp_expires_in_minutes, otp_limit)

	frappe.response['data'] = send_otp_code

