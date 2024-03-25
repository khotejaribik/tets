import frappe
from frappe import _

from data_bridge.data_bridge.authentication.users import user_authentication
from data_bridge.data_bridge.trade_hub.utils.update import (
    get_requested_name, 
    document
)

DOCTYPE = "Partner Customer Profile"

@frappe.whitelist()
def profile():
    
    customer, email_id, mobile_no = user_authentication()

    customer_name = customer.get("name")
    
    requested_name= get_requested_name(DOCTYPE, customer_name)

    requested_data = {
        **frappe.request.form.to_dict(),
    }

    # Check if 'image' is present in uploaded files
    if 'image' in frappe.request.files:
        requested_data['image'] = frappe.request.files['image']

    result = document(DOCTYPE, requested_name, requested_data, customer)

    response = {
        "name": result
    }

    frappe.response['data'] = response
