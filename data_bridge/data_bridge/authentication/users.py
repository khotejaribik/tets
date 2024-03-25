import frappe
from frappe import _

@frappe.whitelist()
def user_authentication():
    email_id = frappe.session.user
    user_exists = frappe.db.exists("User", email_id)

    if not user_exists:
        frappe.throw(_("User not found. Please contact support."), frappe.AuthenticationError)

    user_profile = frappe.db.get_value("User", email_id, ["name", "enabled", "mobile_no"], as_dict=True)
    mobile_no = user_profile.get("mobile_no")

    if not user_profile.get("name"):
        frappe.throw(_("Invalid User"), frappe.AuthenticationError)

    if not user_profile.get("enabled"):
        frappe.throw(_("Sorry. Your account is disabled. Please contact the administrator for assistance."), frappe.AuthenticationError)

    if not mobile_no:
        frappe.throw(_("Invalid mobile number"), frappe.AuthenticationError)

    # The handle_user_is_customer function will throw an error if the customer is not found
    customer = handle_user_is_customer(email_id)
    
    return customer, email_id, mobile_no


def handle_user_is_customer(email_id):
    customer = frappe.db.get_value("Customer", {"email_id": email_id}, ["name", "customer_primary_contact"], as_dict=True)
    
    if not customer:
        # Throw an error if customer is not found
        frappe.throw(_("Customer not found for the user. Please contact support."), frappe.AuthenticationError)

    return customer
