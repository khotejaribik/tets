import frappe
from frappe import _
from data_bridge.data_bridge.authentication.users import user_authentication
from data_bridge.data_bridge.validate.file import validate_file

def process_upload_files(requested_data):
    document = requested_data['document']
    docname = requested_data['docname']
    folder = requested_data['folder']
    is_private = requested_data['is_private']
    attached_to_field = requested_data['attached_to_field']
    attached_to_parent_field = requested_data['attached_to_parent_field']

    files = frappe.request.files.getlist("file")  # Get a list of files

    if not files:
        frappe.throw(_("Files are required. Please attach one or more files."), frappe.ValidationError)

    responses = []

    for file in files:
        content = file.stream.read()
        filename = file.filename

        check_docname_exists = frappe.db.exists(document, docname)

        if not check_docname_exists:
            frappe.throw(_(document + " does not exist: ") + docname, frappe.DoesNotExistError)

        upload_file = frappe.get_doc(
            {
                "doctype": "File",
                "folder": folder,
                "file_name": filename,
                "is_private": is_private,
                "content": content,
                "attached_to_doctype": document,
                "attached_to_name": docname,
                "attached_to_field": attached_to_field,
                "attached_to_parent_field": attached_to_parent_field,
            }
        ).insert(ignore_permissions=True)

        if not upload_file:
            frappe.log_error("Failed to upload file: {}".format(filename))
            frappe.throw(_("Failed to upload file {}. Please try again.").format(filename), frappe.ValidationError)

        file_url = upload_file.file_url

        response = process_file_url_to_document(file_url, document, docname, attached_to_parent_field)
        responses.append(response)

    return responses


def process_file_url_to_document(file_url, document, docname, attached_to_parent_field):
    if document in ["Quotation", "Warranty Claim"] and file_url:
        get_document = frappe.get_doc(document, docname)

        upload_document = frappe.get_doc({
            'doctype': "Sales Attachment",
            'parent': docname,
            'parenttype': document,
            'parentfield': attached_to_parent_field,
            'document': file_url
        })

        get_document.append(attached_to_parent_field, upload_document)

        # Check if payment status is not already set
        if document == "Quotation" and get_document.payment_status != 1:
            get_document.payment_status = 1

        get_document.save(ignore_permissions=True)

        response = {
            "docname": upload_document.parent,
            "file_url": upload_document.document,
        }

        return response


@frappe.whitelist()
def file():
    customer, email_id, mobile_no = user_authentication()

    requested_data = {
        'document': frappe.form_dict.document,
        'docname': frappe.form_dict.docname,
        'files': frappe.request.files,
        'folder': frappe.form_dict.folder,
        'is_private': frappe.form_dict.is_private,
        'attached_to_field': frappe.form_dict.attached_to_field,
        'attached_to_parent_field': frappe.form_dict.attached_to_parent_field,
    }

    validate_file(requested_data)

    responses = process_upload_files(requested_data)

    response_list = []

    for response_data in responses:
        docname = response_data.get('docname')
        file_url = response_data.get('file_url')

        response_item = {
            "docname": docname,
            "file_url": file_url,
        }

        response_list.append(response_item)

    # Construct the final response structure
    final_response = {
        'image': response_list,
    }

    document = requested_data['document']
    docname = requested_data['docname']
    
    if document == "Quotation":
        fetch_payment_status = frappe.db.get_value("Quotation", docname, 'payment_status')
        final_response["payment_status"] = fetch_payment_status

    frappe.response['data'] = final_response
