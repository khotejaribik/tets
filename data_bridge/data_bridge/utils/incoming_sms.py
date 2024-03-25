import frappe

from frappe import _

def get_incoming_sms_setting():
	sms_configuration = frappe.get_doc("Incoming SMS")
	number = sms_configuration.mobile_number
	guest_quotation_message = sms_configuration.guest_quotation_create
	partner_quotation_message = sms_configuration.partner_quotation_create
	lead_message = sms_configuration.lead_create
	pro_partner_message = sms_configuration.pro_partner_create

	return{
		"admin_number": number,
		"guest_quotation_message": guest_quotation_message,
		"partner_quotation_message": partner_quotation_message,
		"lead_message": lead_message,
		"pro_partner_message": pro_partner_message,
	}