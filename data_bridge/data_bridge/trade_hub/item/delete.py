import frappe
from frappe import _

from data_bridge.data_bridge.authentication.users import user_authentication
from data_bridge.data_bridge.trade_hub.utils.delete import (
    get_requested_name, 
    document
)

DOCTYPE = "Partner Item"

@frappe.whitelist()
def item():
   
	customer, email_id, mobile_no = user_authentication()

	customer_name = customer.get("name")

	requested_name = get_requested_name(DOCTYPE, customer_name)

	result = document(DOCTYPE, requested_name, customer_name)

	response = {
		"name": result
	}
	
	frappe.response['data'] = response