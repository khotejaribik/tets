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


def document(doctype, data, customer):
    # Validate data based on doctype
    if doctype == SELLER_DOCTYPE:
        validate_on_create_seller(data)
    elif doctype == CUSTOMER_DOCTYPE:
        validate_on_create_customer(data)
    elif doctype == ITEM_DOCTYPE:
        validate_on_create_item(data)

    # Extract image-related data
    image = data.get("image")
    folder = data.get("folder")
    is_private = data.get("is_private")

    # Remove unnecessary fields
    data.pop("image", None)
    data.pop("folder", None)
    data.pop("is_private", None)

    # Prepare data for creation
    new_data = {
        "doctype": doctype,
        "my_company_name": customer.get("name"),
        **data
    }

    # Create and save the document
    new_document = frappe.get_doc(new_data)
    saved_document = new_document.insert()

    # Handle errors during saving
    if not saved_document:
        frappe.log_error("Failed to save data")
        frappe.throw(
            _("Error while saving data. Please try again later."),
            frappe.ValidationError
        )

    # Retrieve the document name
    docname = saved_document.name

    # Process and save image if available
    if image:
        file_url = file(doctype, image, folder, is_private, docname)
        saved_document.image = file_url
        saved_document.save()

    return docname