from . import __version__ as app_version

app_name = "data_bridge"
app_title = "Data Bridge"
app_publisher = "Ribik Khoteja"
app_description = "API to connect erpnext"
app_email = "ribikkhoteja01@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/data_bridge/css/data_bridge.css"
# app_include_js = "/assets/data_bridge/js/data_bridge.js"

app_include_js = "/assets/data_bridge/js/data_bridge.js"

# include js, css files in header of web template
# web_include_css = "/assets/data_bridge/css/data_bridge.css"
# web_include_js = "/assets/data_bridge/js/data_bridge.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "data_bridge/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
#	"methods": "data_bridge.utils.jinja_methods",
#	"filters": "data_bridge.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "data_bridge.install.before_install"
# after_install = "data_bridge.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "data_bridge.uninstall.before_uninstall"
# after_uninstall = "data_bridge.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "data_bridge.utils.before_app_install"
# after_app_install = "data_bridge.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "data_bridge.utils.before_app_uninstall"
# after_app_uninstall = "data_bridge.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "data_bridge.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
#	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
#	"*": {
#		"on_update": "method",
#		"on_cancel": "method",
#		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

scheduler_events = {
    "cron": {
      "*/5 * * * *": [
          "data_bridge.data_bridge.scheduler_event.otp_status.check_otp_status",
		]
	}
}


# scheduler_events = {
#	"all": [
#		"data_bridge.tasks.all"
#	],
#	"daily": [
#		"data_bridge.tasks.daily"
#	],
#	"hourly": [
#		"data_bridge.tasks.hourly"
#	],
#	"weekly": [
#		"data_bridge.tasks.weekly"
#	],
#	"monthly": [
#		"data_bridge.tasks.monthly"
#	],
# }

# Testing
# -------

# before_tests = "data_bridge.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
#	"frappe.desk.doctype.event.event.get_events": "data_bridge.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "data_bridge.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["data_bridge.utils.before_request"]
# after_request = ["data_bridge.utils.after_request"]

# Job Events
# ----------
# before_job = ["data_bridge.utils.before_job"]
# after_job = ["data_bridge.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
#	{
#		"doctype": "{doctype_1}",
#		"filter_by": "{filter_by}",
#		"redact_fields": ["{field_1}", "{field_2}"],
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_2}",
#		"filter_by": "{filter_by}",
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_3}",
#		"strict": False,
#	},
#	{
#		"doctype": "{doctype_4}"
#	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"data_bridge.auth.validate"
# ]

fixtures = [
      {
        "dt": "Custom Field", 
        "filters": [["name", "in", ["Quotation-payment_details", "Quotation-payment_status", "Quotation-payment_confirmation", "Delivery Note-number_of_box","Delivery Note-packaging_print_note", 
                                    "Delivery Note-transport_note", "Delivery Note-transport_slip", "Delivery Note-transport","Delivery Note-packaging_image", 
                                    "Delivery Note-packaging", "Warranty Claim-received", "Warranty Claim-item_image", "Warranty Claim-images", "Warranty Claim-received_documents",
                                    "Warranty Claim-received_transport_slip", "Warranty Claim-received_packaging_image", "Warranty Claim-column_break_1",
                                    "Warranty Claim-dispatch_documents", "Warranty Claim-dispatch_transport_slip", "Warranty Claim-column_break_2",
                                    "Warranty Claim-dispatch_packaging_image", "Warranty Claim-sent", "Warranty Claim-delivery_note_for_exchanged_item",
                                    "Warranty Claim-delivery_note", "Warranty Claim-resolution_type", "File-attached_to_parent_field",
                                    "Customer-client_name", "Customer-date_of_birth"]]]
      }
]