import frappe
from frappe import _

def file(doctype, files, folder, is_private, docname, fieldname="image"):
  
	file_data = files
	content = file_data.stream.read()
	filename = file_data.filename

	check_doc_exists = frappe.db.exists(doctype, docname)
	
	if not check_doc_exists:
		frappe.throw(_(f"{doctype} does not exist: {docname}"), frappe.DoesNotExistError)

	upload_file = frappe.get_doc({
		"doctype": "File",
		"folder": folder,
		"file_name": filename,
		"is_private": is_private,
		"content": content,
		"attached_to_doctype": doctype,
		"attached_to_name": docname,
		"attached_to_field": fieldname,
	}).insert(ignore_permissions=True)

	if not upload_file:
		frappe.log_error("Failed to upload file")
		frappe.throw(_("Failed to upload file. Please try again."), frappe.ValidationError)

	file_url = upload_file.file_url

	return file_url