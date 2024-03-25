import frappe

from frappe import _
from data_bridge.data_bridge.authentication.users import user_authentication


def get_sales_order_response(customer_name, quotation_name):

	sales_order_details = get_sales_order_details(customer_name, quotation_name)
	sales_order_response = []

	for sales_order in sales_order_details:
		sales_order_data = {
			'name': sales_order['name'],
			'status': sales_order['status'],
			'transaction_date': sales_order['transaction_date'],
			'grand_total': sales_order['grand_total'],
			'per_delivered': sales_order['per_delivered'],
			'per_billed': sales_order['per_billed'],
			'delivery_note': get_delivery_note_response(customer_name, sales_order['name']),
			'sales_invoice': get_sales_invoice_response(customer_name, sales_order['name']),
		}

		sales_order_response.append(sales_order_data)

	return sales_order_response


def get_sales_order_details(customer_name, quotation_name):

	filters = [
		["Sales Order Item","prevdoc_docname","=", quotation_name],
		["customer", "=", customer_name],
		["status", "in", ["To Deliver and Bill", "To Bill", "To Deliver", "Completed"]],
		['docstatus', "=", 1]
	]
	fields = ["name", 'status', 'transaction_date', 'grand_total', 'per_delivered', 'per_billed']

	sales_order_list = frappe.db.get_all(
		"Sales Order",
		filters=filters,
		fields=fields,
		distinct=True,
		order_by = "modified DESC"
	)
	
	return sales_order_list


def get_delivery_note_response(customer_name, sales_order_name):
	
	delivery_note_details = get_delivery_note_details(customer_name, sales_order_name)
	delivery_note_response = []
	
	for delivery_note in delivery_note_details:
		delivery_note_data = {
			'name': delivery_note['name'],
			'status': delivery_note['status'],
			'posting_date': delivery_note['posting_date'],
			'posting_time': delivery_note['posting_time'],
			'grand_total': delivery_note['grand_total'],
			'is_return': delivery_note['is_return'],
			'packaging_image': get_images(delivery_note['name'], "packaging_image"),
			'number_of_box': delivery_note['number_of_box'],
			'transport_image': get_images(delivery_note['name'], "transport_slip"),
			'feedback': get_delivery_note_feedback(customer_name, delivery_note['name']),
		}

		delivery_note_response.append(delivery_note_data)

	return delivery_note_response


def get_delivery_note_details(customer_name, sales_order_name):
	
	filters = [
		["Delivery Note Item","against_sales_order","=", sales_order_name],
		["customer", "=", customer_name],
		["status", "in", ["To Bill", "Completed"]],
		['docstatus', "=", 1]
	]
	fields = ["name", "posting_date", "posting_time", "grand_total", "status", "is_return", "number_of_box"]
	
	delivery_note_list = frappe.db.get_all(
		"Delivery Note",
		filters=filters,
		fields=fields,
		distinct=True,
		order_by = "modified DESC"
	)

	return delivery_note_list


def get_delivery_note_feedback(customer_name, delivery_note_feedback):

	filters = {'company_name': customer_name, 'name': delivery_note_feedback }
	fields = ['posting_date', 'status', 'packed', 'rating', 'feedback']
	
	feedback_data = frappe.db.get_value('Delivery Note Feedback', filters, fields, as_dict=True)
	
	return feedback_data


def get_images(parent_name, parent_field):

	images = frappe.db.get_all(
		"Sales Attachment",
		filters={
			"parent": parent_name,
			"parenttype": "Delivery Note",
			"parentfield": parent_field
		},
		fields=["idx", "document"],
		order_by="idx ASC"
	)

	return [{"idx": image["idx"], "image": image["document"]} for image in images]


def get_sales_invoice_response(customer_name, sales_order_name):

	sales_invoice_details = get_sales_invoice_details(customer_name,sales_order_name)
	sales_invoice_response = []

	for sales_invoice in sales_invoice_details:
		sales_invoice_data = {
			'name': sales_invoice['name'],
			'status': sales_invoice['status'],
			'posting_date': sales_invoice['posting_date'],
			'posting_time': sales_invoice['posting_time'],
			'grand_total': sales_invoice['grand_total'],
			'due_date': sales_invoice['due_date'],
			'is_return': sales_invoice['is_return'],
			'payment_entry': get_payment_response(customer_name, sales_invoice['name'])
		}

		sales_invoice_response.append(sales_invoice_data)

	return sales_invoice_response


def get_sales_invoice_details(customer_name, sales_order_name):
	
	filters = [
		["Sales Invoice Item","sales_order","=", sales_order_name],
		["customer", "=", customer_name],
		["status", "in", ["Paid", "Partly Paid", "Unpaid", "Overdue", "Return"]],
		['docstatus', "=", 1]
	]
	fields= ["name", "posting_date", "posting_time", "due_date", "grand_total", "status", "is_return"]
	sales_invoice_list = frappe.db.get_all(
		"Sales Invoice",
		filters=filters,
		fields=fields,
		distinct=True,
		order_by = "modified DESC"
	)
	
	return sales_invoice_list


def get_payment_response(customer_name, sales_invoice_name):

	payment_details = get_payment_details(customer_name, sales_invoice_name)
	payment_response = []

	for payment_entry in payment_details:
		payment_data = {
			'name': payment_entry['name'],
			'posting_date': payment_entry['posting_date'],
			'mode_of_payment': payment_entry['mode_of_payment'],
			'paid_amount': payment_entry['paid_amount'],
			'reference_no': payment_entry['reference_no'],
			'reference_date': payment_entry['reference_date'],
		}

		payment_response.append(payment_data)

	return payment_response


def get_payment_details(customer_name, sales_invoice_name):
	
	filters = [
		["Payment Entry Reference","reference_name","=", sales_invoice_name],
		["payment_type", "=", "Receive"],
		["party", "=", customer_name],
		["status", "=", "Submitted"],
		['docstatus', "=", 1]
	]
	
	payment_list = frappe.db.get_all(
		"Payment Entry",
		filters=filters,
		fields=["name", "posting_date", "mode_of_payment", "paid_amount", "reference_no", "reference_date"],
		distinct=True,
		order_by = "modified DESC"
	)

	return payment_list


@frappe.whitelist()
def history():
	
	customer, email_id, mobile_no = user_authentication()

	customer_name = customer.get("name")

	start = frappe.form_dict.get('start') or 0
	page_length = frappe.form_dict.get('page_length') or 100
  
	filters = {'party_name': customer_name, 'docstatus': 1, 'status': ['in', ["Ordered", "Partially Ordered"]]}
	fields = ['name', 'status', 'transaction_date', 'grand_total']
	order_by = 'transaction_date DESC'
	
	quotation_list = frappe.db.get_all('Quotation', filters=filters, fields=fields, order_by=order_by, limit_start=start, limit_page_length=page_length)

	quotation_count = frappe.db.count("Quotation", filters=filters)
		
	quotation_response = []
	
	for quotation in quotation_list:
		quotation_name = quotation['name']
		quotation_data = {
			'quotation': {
				'name': quotation['name'],
				'status': quotation['status'],
				'transaction_date': quotation['transaction_date'],
				'grand_total': quotation['grand_total'],
				'sales_order': get_sales_order_response(customer_name, quotation_name)
			},
		}

		quotation_response.append(quotation_data)

	response_data = {
		'list': quotation_response,
		'count': quotation_count,
	}
	
	frappe.response['data'] = response_data
