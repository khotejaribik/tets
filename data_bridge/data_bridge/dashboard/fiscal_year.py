import frappe

from frappe import _
from data_bridge.data_bridge.authentication.users import user_authentication
    
    
def get_fiscal_year():
    fiscal_year = frappe.db.get_all('Fiscal Year', fields=['name', 'year_start_date', 'year_end_date'], order_by = 'creation DESC')
    return fiscal_year
    
    
@frappe.whitelist()    
def read():
    customer, email_id, mobile_no = user_authentication()
    fiscal_year_data = get_fiscal_year()
    frappe.response['data'] = fiscal_year_data