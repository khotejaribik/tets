import frappe

from frappe import _
from data_bridge.data_bridge.authentication.users import user_authentication
	
	
def get_profile(customer_name):
	profile = frappe.db.get_value('Customer', {'name': customer_name}, [
		"customer_name", "image", "client_name", "date_of_birth", "customer_group", "tax_id", "territory", "creation"], as_dict=1)
	return profile
	

@frappe.whitelist()
def read():

	customer, email_id, mobile_no = user_authentication()
	customer_name = customer.get("name")
	  
	customer_profile = get_profile(customer_name)

	response = {
			"image": customer_profile.get("image"),
   			"customer_group": customer_profile.get("customer_group"),
			"email_id": email_id,
			"company_name": customer_name, 
			"customer_name": customer_profile.get("client_name"),
			"date_of_birth": customer_profile.get("date_of_birth"),
			"tax_id": customer_profile.get("tax_id"),
			"mobile_number": mobile_no,
			"territory": customer_profile.get("territory"),
			"creation": customer_profile.get("creation"),
	}

	frappe.response['data'] = response

