import frappe
import json

from frappe import _
from data_bridge.data_bridge.utils.admin_notification import send_notification
from data_bridge.data_bridge.validate.fields import validate_on_create_guest_quotation, validate_item
from data_bridge.data_bridge.validate.otp import validate_otp
from data_bridge.data_bridge.utils.incoming_sms import get_incoming_sms_setting


def process_quotation(data):

	validate_on_create_guest_quotation(data)

	requested_number = data['contact_number']
	otp_code = data['otp']
	
	validate_otp(requested_number, otp_code)

	# Process items
	total_qty = 0
	sub_total = 0
	items = []

	for item in data["items"]:

		item_code = validate_item(item)
		
		# Add item_code to the item
		item["item_code"] = item_code

		item_code = item["item_code"]

		item_price = frappe.db.get_value("Item Price", {"item_code": item_code, 'price_list': 'Standard Selling'}, "price_list_rate")

		qty = item.get("qty")
		qty = int(qty)
		item_amount = item_price * qty

		item.update({
			"price_list_rate": item_price,
			"rate": item_price,
			"amount": item_amount
		})
		total_qty = total_qty + qty
		sub_total = sub_total + item_amount
		

	data.update({
		"total_qty": total_qty,
		"sub_total": sub_total
	})

	# Create quotation document
	keys_to_remove = ["otp"]
	for key in keys_to_remove:
		data.pop(key, None)

	quotation = frappe.get_doc({
		"doctype": "Guest Quotation",
		**data
	})

	# Save quotation
	save_quotation = quotation.insert(ignore_permissions=True)

	if save_quotation:

		guest_name = save_quotation.guest_name
		contact_number = save_quotation.contact_number
		quotation_name = save_quotation.name
		
		incoming_sms = get_incoming_sms_setting()
		admin_number = incoming_sms.get("admin_number")
		guest_quotation_message = incoming_sms.get("guest_quotation_message")

		# send_notification(guest_name, contact_number, quotation_name, admin_number, guest_quotation_message, guest=True)
		
		items = []

		for item in save_quotation.get('items', []):
			item_code = item.get("item_code")
			qty = item.get("qty")
			image = item.get("image")

			items.append({
				"item_code": item_code,
				"qty": qty,
				"image": image
			})

		response_data = {
			"name": save_quotation.name,
			"posting_date": save_quotation.posting_date,
			"guest_name": save_quotation.guest_name,
			"company_name": save_quotation.company_name,
			"pan_vat": save_quotation.pan_vat,
			"address": save_quotation.address,
			"contact_number": save_quotation.contact_number,
			"total_qty": save_quotation.total_qty,
			"items": items
		}
	
		return response_data
		
	else:
		frappe.log_error("Failed to save quotation")
		frappe.throw(_("Error while saving quotation. Please try again later."), frappe.ValidationError)
		

@frappe.whitelist(allow_guest=True)
def quotation():
	try:
		quotation_data = json.loads(frappe.request.data)
	except:
		frappe.throw(_("Invalid JSON data. Failed to decode quotation data."), frappe.ValidationError)

	response_data = process_quotation(quotation_data)
	response = response_data
	frappe.response['data'] = response