import frappe
from frappe import _

def check_otp_status():

    otp_logs = frappe.get_list("Quotation OTP Log", filters={"status": "Active"}, fields=["name", "expires_on"])

    for log in otp_logs:
        expiry_time = log.expires_on
        current_time = frappe.utils.now_datetime()

        if current_time > expiry_time:
            frappe.db.set_value("Quotation OTP Log", log.name, "status", "Expired")
            frappe.db.commit()
