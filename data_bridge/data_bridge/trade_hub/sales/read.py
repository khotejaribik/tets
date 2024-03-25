import frappe
from frappe import _

from data_bridge.data_bridge.authentication.users import user_authentication

DOCTYPE = "Partner Quotation"

def get_quotation_data(quotation_detail, company_name):

	check_quotation_exists = frappe.db.exists(DOCTYPE, {"name": quotation_detail, 'my_company_name': company_name})

	if not check_quotation_exists:
		frappe.throw(_("DoesNotExistError"), frappe.DoesNotExistError)

	quotation_doc = frappe.get_doc(DOCTYPE, quotation_detail)
 
	info_fields = ['name', 'quotation_name', 'transaction_date', 'valid_till']

	calculation_fields = [
		'total_qty', 'total', 'taxable_charge', 'non_taxable_charge', 'sub_total', 'discount_type',
		'discount_percent', 'discount_amount', 'taxable_amount', 'add_tax', 'tax_rate', 'tax_amount', 'net_total', 'grand_total'
	]
 
	item_filters = {'parent': quotation_detail, 'parenttype': DOCTYPE}
 
	item_fields = ["item_master", "website_item","partner_item", "item", "description", "image", "rate", "qty", "amount",
					"warranty", "price_list_rate"]
 
	item_order_by = "idx ASC"
 
	items = frappe.db.get_all("Partner Quotation Item", filters=item_filters, fields=item_fields, order_by=item_order_by)
	
	additional_charges_fields = ["include_tax", "title", "amount"]
 
	additional_charges_order_by = "idx ASC"
 
	additional_charges = frappe.get_all("Partner Quotation Additional Charge", filters=item_filters, fields=additional_charges_fields, order_by=additional_charges_order_by)
	
	customer = {
		'name': quotation_doc.get("customer"),
		'company_name': quotation_doc.get("customer_company_name"),
		'profile': quotation_doc.get("customer_name"),
		'tax_id': quotation_doc.get("customer_tax_id"),
		'address': quotation_doc.get("customer_address"),
		'contact_number': quotation_doc.get("customer_contact_number")
	}
	
	seller = {
		'name': quotation_doc.get("seller"),
		'company_name': quotation_doc.get("seller_company_name"),
		'profile': quotation_doc.get("seller_name"),
		'tax_id': quotation_doc.get("seller_tax_id"),
		'address': quotation_doc.get("seller_address"),
		'contact_number': quotation_doc.get("seller_contact_number"),
	}

	quotation_data = {
		'info': {field: quotation_doc.get(field) for field in info_fields},
		'seller': seller,
		'customer': customer,
		'items': [],
		'additional_charges': additional_charges,
		'calculation': {field: quotation_doc.get(field) for field in calculation_fields}
	}

	if items:
		for item in items:
			item_master = item.get('item_master')

			if item_master == 'Partner Item':
				item_fields = ['partner_item', 'item', 'description', 'image', 'rate', 'qty', 'amount',
								'warranty', 'price_list_rate']
			elif item_master == 'Website Item':
				item_fields = ['website_item', 'item', 'description', 'image', 'rate', 'qty', 'amount',
								'warranty', 'price_list_rate']
			else:
				item_fields = []

			item_data = {field: item.get(field) for field in item_fields}
			quotation_data['items'].append(item_data)

	return quotation_data


def get_quotation_list(company_name):
	
	start = frappe.form_dict.get('start') or 0
	page_length = frappe.form_dict.get('page_length') or 50
	order_by = "modified DESC"

	filters = {
		'my_company_name': company_name,
	}
 
	fields = ['name', 'quotation_name', 'transaction_date', 'valid_till', 'customer_name', 'total_qty', 'grand_total']

	quotation_data = frappe.db.get_all('Partner Quotation', filters=filters, fields=fields,
									order_by=order_by, limit_start=start, limit_page_length=page_length)

	quotation_count = frappe.db.count('Partner Quotation',filters=filters)
	
 
	quotation_response = {
		'list': quotation_data,
		'count': quotation_count,
	}

	return quotation_response


@frappe.whitelist()	
def order():
	
	customer, email_id, mobile_no = user_authentication()
	customer_name = customer.get("name")
 
	quotation_name = frappe.form_dict.name
	
	if quotation_name:
		quotation_data = get_quotation_data(quotation_name, customer_name)
		quotation_response = quotation_data
  	
	else:
		quotation_response = get_quotation_list(customer_name)

	frappe.response['data'] = quotation_response