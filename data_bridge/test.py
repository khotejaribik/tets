import frappe
from frappe import _

# @frappe.whitelist()
# def send_email():
	
# 	current_date = datetime.date.today()
	
# 	print (current_date)
# 	print (type(current_date))
	
# 	data = frappe.db.get_value("Pricing Rule", "PRLE-0125", "valid_from")
	
# 	print (type(data))


	# recipients = "ribik.khoteja@offix.services"
		
	# subject = _("Error while posting depreciation entries")

	# message = "Hello, this is test mail"
	# frappe.sendmail(recipients=recipients, subject=subject, message=message)
 
 
@frappe.whitelist()
def send_email():
	recipients = "ribik.khoteja@offix.services"
	sender = "ribikkhoteja5@gmail.com"
	subject = "Test Mail"
	message = "Hi, this is test mail message"

	data = frappe.enqueue(
		queue="short",
		method=frappe.sendmail,
		recipients=recipients,
		subject=subject,
		message=message,
		now=True,
	)
	
@frappe.whitelist()
# Get default selling price list
def get_selling_price_list():
	selling_price_list = frappe.db.get_single_value ("Selling Settings", "selling_price_list")
	print (selling_price_list)
 
	# frappe.enqueue(
	# 			queue="short",
	# 			method=frappe.sendmail,
	# 			recipients=recipients,
	# 			subject=subject,
	# 			message=message,
	# 			now=True,
	# 			reference_doctype="Process Statement Of Accounts",
	# 			reference_name=document_name,
	# 			attachments=attachments,
	# 		)
			
   
	# data = frappe.sendmail(
	# 	recipients="ribik.khoteja@offix.services",
	# 	message= "Hi, this is test mail message",
	# 	subject= "Test Mail",
	# 	now = True
	# )
 
			