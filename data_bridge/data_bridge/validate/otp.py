import frappe
from frappe import _

#Validate OTP code
def validate_otp(requested_number, otp):
	current_time = frappe.utils.now_datetime()
	check_otp_log = frappe.db.exists("Quotation OTP Log", {"requested_number": requested_number})

	if check_otp_log:
		login_log = frappe.get_doc('Quotation OTP Log', check_otp_log)
		fetched_otp = login_log.otp_code
		sent_on = login_log.sent_on
		time = login_log.time
		
		if otp != fetched_otp:
			frappe.throw(_("Invalid OTP. Please enter the correct OTP."), frappe.AuthenticationError)

		diff = current_time - sent_on
		check_time = int(diff.total_seconds() / 60)

		if check_time >= time:
			frappe.throw(_("OTP has expired. Please request a new OTP."), frappe.AuthenticationError)

	else:
		frappe.throw(_("Invalid OTP. Please request a new OTP."), frappe.AuthenticationError)