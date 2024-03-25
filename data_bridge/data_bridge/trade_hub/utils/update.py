import frappe
from frappe import _

from data_bridge.data_bridge.validate.fields import (
    validate_on_create_seller,
    validate_on_create_customer,
    validate_on_create_item
)
from data_bridge.data_bridge.trade_hub.utils.upload import file

SELLER_DOCTYPE = "Partner Seller Profile"
CUSTOMER_DOCTYPE = "Partner Customer Profile"
ITEM_DOCTYPE = "Partner Item"


def get_requested_name(DOCTYPE, customer_name):
    requested_profile = frappe.request.args.get("name")
    
    if not requested_profile:
        frappe.throw(_("Profile missing."), frappe.ValidationError)

    filters = {'my_company_name':customer_name, 'name':requested_profile}
    
    profile_exists = frappe.db.exists(DOCTYPE, filters)
    
    if not profile_exists:
        frappe.throw(_("Profile not found: ") + requested_profile, frappe.DoesNotExistError)

    return requested_profile


def document(DOCTYPE, document_name, update_data, customer):
    # Validate data based on doctype
    if DOCTYPE == SELLER_DOCTYPE:
        validate_on_create_seller(update_data)
    elif DOCTYPE == CUSTOMER_DOCTYPE:
        validate_on_create_customer(update_data)
    elif DOCTYPE == ITEM_DOCTYPE:
        validate_on_create_item(update_data)

    # Extract image-related data
    image = update_data.get("image")
    folder = update_data.get("folder")
    is_private = update_data.get("is_private")

    # Remove unnecessary fields
    update_data.pop("image", None)
    update_data.pop("folder", None)
    update_data.pop("is_private", None)

    # Prepare data for updating
    update_data.update({
        "doctype": DOCTYPE,
        "my_company_name": customer.get("name")
    })

    # Get the existing document
    existing_document = frappe.get_doc(DOCTYPE, document_name)

    # Save the updated document
    try:
        existing_document.update(update_data)
        existing_document.save()
    except Exception as e:
        frappe.log_error(f"Failed to update data: {e}")
        frappe.throw(_("Error while updating data. Please try again later."), frappe.ValidationError)

    # Process and save image if available
    if image:
        file_url = file(DOCTYPE, image, folder, is_private, document_name)
        existing_document.image = file_url
        existing_document.save()

    return existing_document.name
