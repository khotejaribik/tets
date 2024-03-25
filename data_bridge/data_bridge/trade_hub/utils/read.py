import frappe
from frappe import _

def trade_data(doctype, filters, fields, order_by):

	start = frappe.form_dict.get('start') or 0
	page_length = frappe.form_dict.get('page_length') or 100
 
	data = frappe.db.get_all(doctype, filters=filters, fields=fields, order_by=order_by, limit_start=start, limit_page_length=page_length)
	count = frappe.db.count(doctype, filters=filters)

	return {'data': data, 'count': count}
