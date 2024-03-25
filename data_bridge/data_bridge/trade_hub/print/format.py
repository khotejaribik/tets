import frappe

from frappe import _
from data_bridge.data_bridge.authentication.users import user_authentication


def get_quotation_template():
    # Specify filters to get the desired child table data
    filters = {"parent": "Partner Quotation Template", "parentfield": "template"}

    # Fetch child table data using frappe.get_all
    child_table_data = frappe.db.get_all(
        "Partner Quotation Template Table",
        filters=filters,
        fields=["idx", "image", "print_format"],
        order_by = "idx ASC"
    )

    return child_table_data


@frappe.whitelist()
def read():
	customer, email_id, mobile_no = user_authentication()

	quotation_template = get_quotation_template()

	response = quotation_template

	frappe.response['data'] = response