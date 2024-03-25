import frappe
from frappe import _

from data_bridge.data_bridge.validate.fields import validate_on_create_custom_order


def validate_profile(seller, customer):
    for profile, profile_type in [(seller, "Partner Seller Profile"), (customer, "Partner Customer Profile")]:
        if not frappe.db.exists(profile_type, profile):
            frappe.throw(_(f"{profile_type} does not exist."), frappe.DoesNotExistError)


def validate_item(item):
    website_item = frappe.get_value("Website Item", item, ["item_code", "short_description", "website_image"], as_dict=True)
    partner_item = frappe.get_value("Partner Item", item, ["item_name", "rate", "description", "image", "warranty"], as_dict=True)

    if not website_item and not partner_item:
        frappe.throw(_("Invalid item code: ") + item, frappe.DoesNotExistError)

    data_source = website_item if website_item else partner_item
    return {
        "item_master": "Website Item" if website_item else "Partner Item",
        "website_item": item if website_item else None,
        "partner_item": item if partner_item else None,
        "item": data_source.get("item_code") or data_source.get("item_name"),
        "price_list_rate": data_source.get("rate") or frappe.db.get_value("Item Price", filters={"item_code": data_source.get('item_code'), 'price_list': 'Standard Selling'}, fieldname="price_list_rate"),
        "description": data_source.get("short_description") or data_source.get("description"),
        "image": data_source.get("website_image") or data_source.get("image"),
        "warranty": data_source.get("warranty"),
    }


def calculate_item(item):
    rate = float(item.get("rate"))
    qty = item.get("qty")
    item["amount"] = rate * qty
    return {'qty': qty, 'amount': item["amount"]}


def calculate_additional_charges(additional_charges):
    taxable_charges = non_taxable_charges = 0
    
    for charge in additional_charges:
        amount, include_tax = charge.get("amount"), charge.get("include_tax")
        if include_tax == 1:
            taxable_charges += amount
        elif include_tax == 0:
            non_taxable_charges += amount
        else:
            frappe.throw("Invalid value for include_tax.")

    return taxable_charges, non_taxable_charges


def calculate_discount(discount_type, discount, sub_total):
    if discount_type == "Percentage" and discount:
        taxable_amount = sub_total * ((100 - discount) / 100)
        return taxable_amount, discount
    elif discount_type == "Amount" and discount:
        taxable_amount = sub_total - discount
        return taxable_amount, discount
    else:
        return sub_total, 0


def calculate_tax_and_net_total(add_tax, tax_rate, taxable_amount):
    if add_tax == 1:
        tax_amount = taxable_amount * (tax_rate / 100)
        net_total = taxable_amount + tax_amount
        return tax_amount, net_total
    elif add_tax == 0:
        return 0, taxable_amount
    else:
        return 0, taxable_amount


def calculate_grand_total(net_total, non_taxable_charges):
    return net_total + non_taxable_charges


def calculation(quotation_data, total_qty, total):
    additional_charges = quotation_data.get("additional_charge")
    taxable_charges, non_taxable_charges = calculate_additional_charges(additional_charges)

    sub_total = total + taxable_charges if taxable_charges else total

    discount_type, discount = quotation_data.get("discount_type"), quotation_data.get("discount")

    taxable_amount, discount_applied = calculate_discount(discount_type, discount, sub_total)

    add_tax, tax_rate = quotation_data.get("add_tax"), quotation_data.get("tax_rate", 0)
    tax_amount, net_total = calculate_tax_and_net_total(add_tax, tax_rate, taxable_amount)

    grand_total = calculate_grand_total(net_total, non_taxable_charges)

    quotation_data.update({
        "total_qty": total_qty,
        "total": total,
        "taxable_charge": taxable_charges,
        "non_taxable_charge": non_taxable_charges,
        "sub_total": sub_total,
        "taxable_amount": taxable_amount,
        "tax_amount": tax_amount,
        "net_total": net_total,
        "grand_total": grand_total,
        "discount_amount": discount_applied if discount_type == "Amount" else 0,
        "discount_percent": discount_applied if discount_type == "Percentage" else 0,
    })

    return quotation_data


def set_default_values(quotation_data):
    keys_to_set_default = ["add_tax", "tax_rate", "discount_type", "discount"]

    for key in keys_to_set_default:
        if key not in quotation_data:
            if key in ["add_tax", "tax_rate", "discount"]:
                quotation_data[key] = 0
            elif key == "discount_type":
                quotation_data[key] = ""


def process_quotation(quotation_data, customer):
    seller_profile, customer_profile = quotation_data.get("seller"), quotation_data.get("customer")

    validate_on_create_custom_order(quotation_data)
    validate_profile(seller_profile, customer_profile)

    total_qty, total = 0, 0

    for item in quotation_data.get("items", []):
        item_name = item.get("name")
        data = validate_item(item_name)
        item.update(data)
        item.pop("name", None)  # Remove the "name" key from the item dictionary
        result = calculate_item(item)
        total_qty += result['qty']
        total += result['amount']
        
    # Set default values for certain keys
    set_default_values(quotation_data)        
    
    # Handle additional charges array
    if "additional_charge" not in quotation_data:
        quotation_data["additional_charge"] = []

    quotation_data = {
        "doctype": "Partner Quotation",
        "my_company_name": customer.get("name"),
        **quotation_data
    }

    quotation_data = calculation(quotation_data, total_qty, total)
    
    return quotation_data