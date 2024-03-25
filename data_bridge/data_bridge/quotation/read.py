import frappe
import json

from frappe import _
from data_bridge.data_bridge.authentication.users import user_authentication

#Payment details
def get_payment_details(quotation_name):
	filters = {
		'parent': quotation_name,
		'parenttype': 'Quotation',
		'parentfield': 'payment_details'
	}
	fields = ['idx', 'document']
	order_by = 'idx asc'
	payment_details = frappe.db.get_all('Sales Attachment', filters=filters, fields=fields, order_by=order_by)
	return payment_details


#Views
def get_quotation_view_logs(name):
	filters = {'reference_doctype': 'Quotation', 'reference_name': name}
	fields = ['creation', 'viewed_by', 'reference_name']
	order_by = 'creation desc'
	quotation_view_logs = frappe.db.get_all('View Log', filters=filters, fields=fields, order_by=order_by)
	return quotation_view_logs


def get_quotation_views(name):
	latest_creations = {}
	quotation_view_logs = get_quotation_view_logs(name)
	for quotation_view_log in quotation_view_logs:
		if quotation_view_log.reference_name not in latest_creations:
			latest_creations[quotation_view_log.reference_name] = {}
		if quotation_view_log.viewed_by not in latest_creations[quotation_view_log.reference_name] or quotation_view_log.creation > latest_creations[quotation_view_log.reference_name][quotation_view_log.viewed_by]:
			latest_creations[quotation_view_log.reference_name][quotation_view_log.viewed_by] = quotation_view_log.creation

	quotation_views = []
	for viewed_by, creation in latest_creations.get(name, {}).items():
		user = frappe.get_doc('User', viewed_by)
		user_image = user.user_image if user and user.user_image else None
		full_name = user.full_name if user else None
		quotation_views.append({
			'creation': creation,
			'viewed_by': viewed_by,
			'reference_name': name,
			'user_image': user_image,
			'full_name': full_name
		})
	return quotation_views


#Versions
def get_quotation_versions(quotation_name):
	filters = {'ref_doctype': 'Quotation', 'docname': quotation_name}
	fields = ['name', 'owner', 'creation', 'data', 'docname']
	order_by = 'creation desc'
	quotation_version = frappe.db.get_all('Version', filters=filters, fields=fields, order_by=order_by)
	return quotation_version


def format_quotation_version(data):

	processed_list = []

	for category, data_dict in data:
		# Check if the category is 'items'
		if category == 'items':
			# Extract required fields from the dictionary
			idx = data_dict.get('idx')
			item_code = data_dict.get('item_code')
			item_group = data_dict.get('item_group')
			brand = data_dict.get('brand')
			qty = data_dict.get('qty')
			rate = data_dict.get('rate')
			amount = data_dict.get('amount')
			parent = data_dict.get('parent')
			discount_amount = data_dict.get('discount_amount')
			discount_percentage = data_dict.get('discount_percentage')

			# Create a dictionary for the item and append it to added_list
			item_dict = {
				'idx': idx, 'item_code': item_code, 'item_group': item_group, 'brand': brand, 'qty': qty,
				'rate': rate, 'amount': amount, 'parent': parent, 'discount_amount': discount_amount,
				'discount_percentage': discount_percentage
			}
			processed_list.append(["items", item_dict])

		if category == 'taxes':
			idx = data_dict.get('idx')
			description = data_dict.get('description')
			rate = data_dict.get('rate')
			tax_amount = data_dict.get('tax_amount')

			tax_dict = {'idx': idx, 'description': description, 'rate': rate, 'tax_amount': tax_amount}

			processed_list.append(["taxes", tax_dict])

		return processed_list	


def quotation_version_response(quotation_version):

	data = json.loads(quotation_version.get('data'))

	added_items = data.get('added', [])
	added_list = format_quotation_version(added_items)

	removed_items = data.get('removed', [])
	removed_list = format_quotation_version(removed_items)

	formatted_data = {
		"added": added_list,
		"changed": data['changed'],
		"removed": removed_list,
		"row_changed": data['row_changed'],
	}

	return {
		'name': quotation_version['name'],
		'owner': quotation_version['owner'],
		'quotation': quotation_version['docname'],
		'creation': quotation_version['creation'],
		'data': formatted_data
	}

	
# Info
def get_quotation_data(customer_name, quotation_name):

	filters = {
		'party_name': customer_name,
		'name': quotation_name,
	}
	fields = ['name', 'transaction_date', 'total_qty', 'grand_total', 'status', 'party_name',
			  'contact_email', 'payment_status', 'payment_confirmation', 'modified', 'modified_by']
	
	data = frappe.db.get_value('Quotation', filters, fields, as_dict=True)
	
	if not data:
		frappe.throw(_("Quotation not found"), frappe.DoesNotExistError)
		
	return data


def get_quotation_items(name):

	filters = {'parent': name, 'parenttype': 'Quotation'}
	fields = ['name', 'image', 'item_code', 'item_group', 'qty', 'rate', 'amount', 'stock_uom', 'pricing_rules']
	order_by = 'idx asc'
	doc = frappe.db.get_all('Quotation Item', filters=filters, fields=fields, order_by=order_by)
	items = []

	for item in doc:
		pricing_rules_flag, selected_pricing_rule = get_item_pricing_rule(item)
		web_item_name = frappe.db.get_value('Website Item', {'item_code': item.get('item_code')}, 'name')
		item_data = {
			'image': item.get('image'),
			'web_item_name': web_item_name,
			'item_code': item.get('item_code'),
			'item_group': item.get('item_group'),
   			'stock_uom': item.get('stock_uom'),
			'qty': item.get('qty'),
			'rate': item.get('rate'),
			'amount': item.get('amount'),
			'pricing_rule': pricing_rules_flag,
			'pricing_rule_name': selected_pricing_rule.get('pricing_rule_name'),
			'selected_pricing_rule': selected_pricing_rule['selected_pricing_rule'],
		}
		items.append(item_data)

	return items


def get_item_pricing_rule(item):
	pricing_rules = item.get("pricing_rules")
	uom = item.get("stock_uom")
	web_item_name = None
	pricing_rules_flag = False
	selected_pricing_rule = []

	if pricing_rules:
		web_item_name = frappe.db.get_value("Website Item", {'item_code': item.get('item_code')}, 'name')
		if web_item_name:
			pricing_rules_list = json.loads(pricing_rules.replace('\n', ''))
			pricing_rule_details = get_selected_pricing_rule(uom, pricing_rules_list)
			web_item_name = web_item_name + '_PRLE'
			pricing_rules_flag = True
			selected_pricing_rule = pricing_rule_details['selected_pricing_rule']

	return pricing_rules_flag, {
		'pricing_rule_name': web_item_name,
		'selected_pricing_rule': selected_pricing_rule,
	}


def get_selected_pricing_rule(uom, pricing_rules_list):
	pricing_rule = frappe.db.get_value("Pricing Rule", pricing_rules_list, ["min_qty", "max_qty"], as_dict=True)
	min_qty = pricing_rule.get("min_qty")
	max_qty = pricing_rule.get("max_qty")

	return {
		'selected_pricing_rule': {'uom_name': f"{int(min_qty)}-{int(max_qty)} {uom}"},
	}


@frappe.whitelist()	
def quotation():
	
	customer, email_id, mobile_no = user_authentication()

	customer_name = customer.get("name")
	
	quotation_name = frappe.form_dict.name
	
	quotation_response = {}

	if quotation_name:
		check_quotation_exists = frappe.db.exists("Quotation", {'party_name':customer_name, 'name':quotation_name})
	
		if not check_quotation_exists:
			frappe.throw(_("Quotation does not exists"), frappe.DoesNotExistError)
			
		data = get_quotation_data(customer_name, quotation_name)
		  
		doc = get_quotation_items(quotation_name)
		quotation_views = get_quotation_views(quotation_name)
		quotation_versions = get_quotation_versions(quotation_name)
		quotation_versions_response = [quotation_version_response(version) for version in quotation_versions]
		doc_attachments = get_payment_details(quotation_name)
		
		quotation_response.update({
			'info': data,
			'items': doc,
			'views': quotation_views,
			'versions': quotation_versions_response,
			'payment': doc_attachments
		})
		
		frappe.response['data'] =  quotation_response
	
	else:
		
		start = frappe.form_dict.get('start') or 0
		page_length = frappe.form_dict.get('page_length') or 100
		
		filters = {
			'party_name': customer_name,
			'status': ['not in', ["Cancelled"]],
		}

		order_by = 'modified desc'
		
		quotation_data = frappe.db.get_all('Quotation', filters=filters,
								order_by=order_by, limit_start=start, limit_page_length=page_length)

		quotation_count = frappe.db.count('Quotation', filters=filters)

		quotation_response = []

		for data in quotation_data:
			quotation_name = data.get("name")
			quotation_info = get_quotation_data(customer_name, quotation_name)
			quotation_views = get_quotation_views(quotation_name)
			quotation_versions = get_quotation_versions(quotation_name)
			quotation_versions_response = [quotation_version_response(version) for version in quotation_versions]

			payment_details = get_payment_details(quotation_name)

			# Create a dictionary for each quotation with the required structure
			quotation_dict = {
				"info": quotation_info,
				"views": quotation_views,
				"versions": quotation_versions_response,
				"payment": payment_details
			}

			quotation_response.append(quotation_dict)

		frappe.response['data'] = {
			"list": quotation_response,
			"count": quotation_count
		}