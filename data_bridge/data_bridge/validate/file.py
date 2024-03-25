import frappe
from frappe import _

#File validation         
def validate_file(requested_data):
    required_fields = ["document", "docname", "files", "folder", "is_private", "attached_to_field", "attached_to_parent_field"]
    missing_fields = []

    for field in required_fields:
        if not requested_data.get(field):
            missing_fields.append(field)

    if missing_fields:
        missing_fields_str = ", ".join(missing_fields)
        frappe.throw(f"The following fields are required: {missing_fields_str}", frappe.ValidationError)
