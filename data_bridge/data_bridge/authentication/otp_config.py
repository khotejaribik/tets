import frappe
import requests

from frappe import _

def get_company_name():
	company = frappe.db.get_single_value ("Global Defaults", "default_company")
	return company


def get_sms_settings():
	# Assuming there is only one SMS Settings document
	sms_settings = frappe.get_doc("SMS Settings")

	# Print parent table fields
	sms_gateway_url = sms_settings.sms_gateway_url
	message_parameter = sms_settings.message_parameter
	receiver_parameter = sms_settings.receiver_parameter

	# Print child table values
	parameters = sms_settings.get("parameters")  # Assuming "parameters" is the fieldname for the child table

	if parameters:
		parameters_list = []
		for parameter in parameters:
			key = parameter.parameter
			value = parameter.value
			
			parameters_list.append({"parameter": key, "value": value})

		return {"sms_gateway_url": sms_gateway_url, "message_parameter": message_parameter, "receiver_parameter": receiver_parameter, "parameters": parameters_list}
		
	else:
		frappe.throw(_("An error occurred while sending the SMS. Please contact the administrator for assistance."), frappe.AuthenticationError)


def get_otp_settings(for_guest=False):
    otp_settings = frappe.get_doc("Quotation OTP Settings")
    
    otp_length = otp_settings.otp_length
    otp_expires_in_minutes = otp_settings.otp_expires_in

    if for_guest:
        return otp_length, otp_expires_in_minutes, otp_settings.disable_login, otp_settings.otp_limit

    return otp_length, otp_expires_in_minutes


def generate_otp_code(otp_length):
    timestamp = int(frappe.utils.nowtime().replace(':', '').replace('.', ''))
    random_number = ((timestamp * 7) + 3) % (10 ** otp_length)
    otp_code = str(random_number).zfill(otp_length)
    return otp_code


def config_process_otp_code(settings, text, mobile_no):
	# Extract values from settings
	sms_gateway_url = settings.get('sms_gateway_url', '')
	message_parameter = settings.get('message_parameter', '')
	receiver_parameter = settings.get('receiver_parameter', '')
	
	parameters = {param['parameter']: param['value'] for param in settings.get('parameters', [])}

	# Assuming requested_number and send_message are already defined
	data = {
		message_parameter : text,
		receiver_parameter : mobile_no,
		'responsetype': 'json', # This may vary with sms provider
		**parameters  # Unpack parameters into the data dictionary
	}

	# Make the POST request
	response = requests.post(sms_gateway_url, data=data)

	# Parse the JSON response
	response_json = response.json()

	# Print the 'response_message' field
	response_message = response_json.get("response_message")
	sms_shootid = response_json.get("sms_shootid")

	return{
		'response_message': response_message,
		'sms_shootid': sms_shootid
	}