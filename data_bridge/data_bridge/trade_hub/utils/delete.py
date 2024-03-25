import frappe
from frappe import _


def get_requested_name(DOCTYPE, customer_name):
	
	if frappe.request.method == "DELETE":
		
		requested_name = frappe.request.args.get("name")
	
		if not requested_name:
			frappe.throw(_("Name missing."), frappe.ValidationError)

		filters = {'my_company_name':customer_name, 'name':requested_name}
	
		profile_exists = frappe.db.exists(DOCTYPE, filters)

		if not profile_exists:
			frappe.throw(_("Data not found: ") + requested_name, frappe.DoesNotExistError)

		return requested_name
	
	else:
		frappe.throw(_("Method not allowed. Please use the DELETE method."), frappe.ValidationError)


def document(DOCTYPE, document_name, customer):
    
    document = frappe.get_doc(DOCTYPE, document_name)
    
    if document.my_company_name != customer:
        frappe.throw(_("You are not allowed to delete the document."), frappe.AuthenticationError)

    # Save the updated document
    try:
        document.delete()
        frappe.db.commit()
        
    except Exception as e:
        frappe.log_error("Failed to delete data: " + str(e))
        frappe.throw(_("Error while deleting data. Please try again later."), frappe.ValidationError)

    return document_name
