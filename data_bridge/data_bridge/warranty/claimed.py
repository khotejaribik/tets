import frappe
from frappe import _
from data_bridge.data_bridge.authentication.users import user_authentication

doctype = "Warranty Claim"

def get_images(parent_name, parent_field):

	images = frappe.db.get_all(
		"Sales Attachment",
		filters={
			"parent": parent_name,
			"parenttype": "Warranty Claim",
			"parentfield": parent_field
		},
		fields=["idx", "document"],
		order_by="idx ASC"
	)

	return [{"idx": image["idx"], "image": image["document"]} for image in images]


def get_warranty_data(warranty_data):
	response = {
		'name': warranty_data.get("name"),
  		'complaint_date': warranty_data.get("complaint_date"),
		'serial_no': warranty_data.get("serial_no"),
		'item_code': warranty_data.get("item_code"),
		'status': warranty_data.get("status"),
		'received': warranty_data.get("received"),
		'sent': warranty_data.get("sent"),
  		'complaint': warranty_data.get("complaint"),
		'resolution_type': warranty_data.get("resolution_type"),
		'resolution_date': warranty_data.get("resolution_date"),
		'resolution_details': warranty_data.get("resolution_details"),
		'exchanged_delivery_note': warranty_data.get("delivery_note"),
		'item_images': get_images(warranty_data.get("name"), "images"),
		'received_transport_slip': get_images(warranty_data.get("name"), "received_transport_slip"),
		'received_packaging_image': get_images(warranty_data.get("name"), "received_packaging_image"),
		'dispatch_transport_slip': get_images(warranty_data.get("name"), "dispatch_transport_slip"),
		'dispatch_packaging_image': get_images(warranty_data.get("name"), "dispatch_packaging_image"),
	}
	return response


@frappe.whitelist()
def warranty():
	customer, email_id, mobile_no = user_authentication()
	customer_name = customer.get("name")

	warranty_claimed_name = frappe.form_dict.name
	
	if warranty_claimed_name:
		warranty_data = frappe.get_doc("Warranty Claim", warranty_claimed_name)

		if warranty_data.get("customer") != customer_name and warranty_data.get("customer_name") != customer_name:
			frappe.throw(_("Unauthorized access to warranty claim"), frappe.PermissionError)

		response = get_warranty_data(warranty_data)
		
	else:
		
		start = frappe.form_dict.get('start') or 0
		page_length = frappe.form_dict.get('page_length') or 100
  
		filters = {
			'customer': customer_name,
			'customer_name': customer_name,
		}

		fields = ['name', 'serial_no', 'item_code', 'status', 'complaint_date', 'resolution_date', 'resolution_type', 'received', 'sent']
		order_by = 'modified DESC'

		warranty_claimed_list = frappe.db.get_all(doctype, filters=filters, fields=fields, order_by=order_by, limit_start=start, limit_page_length=page_length)

		warranty_claimed_count = frappe.db.count(doctype, filters=filters)

		response = {
			'list': warranty_claimed_list,
			'count': warranty_claimed_count
		}

	frappe.response['data'] = response