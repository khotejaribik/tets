import frappe
from frappe import _
from data_bridge.data_bridge.authentication.users import user_authentication


def get_warranty_claim(serial_no):
	filters = {
		'serial_no': serial_no
	}
	fields = ["name", "status"]
	warranty_claim = frappe.db.get_value("Warranty Claim", filters, fields, as_dict=True)
	return warranty_claim


@frappe.whitelist()
def serial():
	customer, email_id, mobile_no = user_authentication()
	customer_name = customer.get("name")

	start = frappe.form_dict.get('start') or 0
	page_length = frappe.form_dict.get('page_length') or 100
  
	filters = {
		'customer_name': customer_name,
		'status': 'Delivered',
	}

	fields = ['serial_no', 'item_code', 'delivery_document_no', 'delivery_date', 'warranty_expiry_date', 'maintenance_status', 'warranty_period']
	order_by = 'delivery_date desc'

	serial_no_list = frappe.db.get_all("Serial No", filters=filters, fields=fields, order_by=order_by, limit_start=start, limit_page_length=page_length)

	response_data = []

	for serial_data in serial_no_list:
		serial_no = serial_data.get("serial_no")
		warranty_claimed = get_warranty_claim(serial_no)
		
		# Move the declaration of warranty_name inside the loop
		warranty_name = None  # Default value if warranty_claimed is None
		status = None  # Default value if warranty_claimed is None
		
		if warranty_claimed:
			warranty_name = warranty_claimed.get("name")
			status = warranty_claimed.get("status")
			
		maintenance_status = status if status in ["Open", "Work In Progress"] else serial_data.get("maintenance_status")
				
		response_data.append({
			'serial_no': serial_data.get("serial_no"),
			'item_code': serial_data.get("item_code"),
			'delivery_document_no': serial_data.get("delivery_document_no"),
			'delivery_date': serial_data.get("delivery_date"),
			'warranty_expiry_date': serial_data.get("warranty_expiry_date"),
			'maintenance_status': maintenance_status,
			'warranty_period': serial_data.get("warranty_period"),
			'warranty_claimed': warranty_name
		})

	serial_count = frappe.db.count("Serial No", filters=filters)

	response = {
		'list': response_data,
		'count': serial_count
	}

	frappe.response['data'] = response
