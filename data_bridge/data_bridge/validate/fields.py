import frappe
from frappe import _


# Guest quotation
def validate_on_create_guest_quotation(quotation_data):
	required_fields = ['otp', 'guest_name', 'company_name', 'pan_vat', 'contact_number', 'address', 'items']
	optional_fields = None  # No optional fields for create
	validate_fields(required_fields, optional_fields, quotation_data)


# Create quotation
def validate_on_create_quotation(quotation_data):
	required_fields = ['items', 'otp']
	optional_fields = None 
	validate_fields(required_fields, optional_fields, quotation_data)


# Update quotation
def validate_on_update_quotation(quotation_data):
	required_fields = ['items']
	optional_fields = None
	validate_fields(required_fields, optional_fields, quotation_data)


# Create warranty 
def validate_on_create_warranty(warranty_data):
	required_fields = ['serial_no', 'complaint']
	optional_fields = None
	validate_fields(required_fields, optional_fields, warranty_data)


# Create partner seller profile 
def validate_on_create_seller(profile):
	required_fields = ['company_name', 'seller_name']
	optional_fields = ['image', 'designation', 'tax_id', 'address', 'contact_number', 'email', 'notes', 'folder', 'is_private']
	validate_fields(required_fields, optional_fields, profile)
	
	
# Create partner customer profile 
def validate_on_create_customer(profile):
	required_fields = ['customer_name']
	optional_fields = ['company_name', 'image', 'designation', 'tax_id', 'address', 'contact_number', 'email', 'notes', 'folder', 'is_private']
	validate_fields(required_fields, optional_fields, profile)
		

# Create partner item 
def validate_on_create_item(item):
	required_fields = ['item_name', 'rate']
	optional_fields = ['image', 'description', 'warranty', 'folder', 'is_private']
	validate_fields(required_fields, optional_fields, item)


# Create partner sales order 
def validate_on_create_custom_order(item):
	required_fields = ['quotation_name', 'transaction_date', 'seller', 'customer', 'items']
	optional_fields = ['valid_till', 'additional_charge', 'discount_type', 'discount', 'add_tax', 'tax_rate', 'terms_conditions', 'notes']
	validate_fields(required_fields, optional_fields, item)   
			

# Create feedback
def validate_on_create_feedback(item):
	required_fields = ['status']
	optional_fields = ['packed', 'rating', 'feedback']
	validate_fields(required_fields, optional_fields, item)   
			
     				   
# Validating fields
def validate_fields(required_fields, optional_fields, requested_data):
	missing_fields = []
	unrecognized_fields = []

	# Check required fields
	for field in required_fields:
		if field not in requested_data:
			missing_fields.append(field)
   
	# Check unrecognized fields
	for field in requested_data:
		if field not in required_fields and field not in optional_fields:
			unrecognized_fields.append(field)
			
	# Check fields within "items"
	if "items" in requested_data:
		for item in requested_data["items"]:
			# Check required fields for each item
			item_required_fields = ['name', 'qty']
			item_optional_fields = ['rate']
			for field in item_required_fields:
				if field not in item:
					missing_fields.append(f"items.{field}")

			# Check unrecognized fields for each item
			for field in item:
				if field not in item_required_fields and field not in item_optional_fields:
					unrecognized_fields.append(f"items.{field}")


	# Check fields within "items"
	if "additional_charge" in requested_data:
		for item in requested_data["additional_charge"]:
			# Check required fields for each item
			item_required_fields = ['include_tax', 'title', 'amount']
			for field in item_required_fields:
				if field not in item:
					missing_fields.append(f"additional_charge.{field}")

			# Check unrecognized fields for each item
			for field in item:
				if field not in item_required_fields:
					unrecognized_fields.append(f"additional_charge.{field}")


	# Raise ValidationError if there are missing or unrecognized fields
	if missing_fields or unrecognized_fields:
		error_message = ""
		if missing_fields:
			missing_fields_str = ', '.join(missing_fields)
			error_message += f"The following fields are required: {missing_fields_str}. "
		if unrecognized_fields:
			unrecognized_fields_str = ', '.join(unrecognized_fields)
			error_message += f"The following fields are unrecognized: {unrecognized_fields_str}"

		frappe.throw(error_message, frappe.ValidationError)
  

#Item validation
def validate_item(item):
	web_item = item.get("name")
	qty = item.get("qty")
	
	if not web_item:
		frappe.throw(_("Item code is required"), frappe.ValidationError)
	
	if not qty:
		frappe.throw(_("Quantity is required for item: ") + web_item, frappe.ValidationError)

	# Assuming "Website Item" is a doctype and you want to check if the item exists
	check_item = frappe.get_doc("Website Item", web_item)
	
	if check_item:
		item_code = check_item.item_code
		return item_code
	else:
		frappe.throw(_("Invalid item: ") + web_item, frappe.DoesNotExistError)
   