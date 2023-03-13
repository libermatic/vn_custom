# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__

app_name = "vn_custom"
app_version = __version__
app_title = "VN Custom"
app_publisher = "Libermatic"
app_description = "Customizations for VN"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "info@libermatic.com"
app_license = "MIT"

error_report_email = "support@libermatic.com"

fixtures = [
    {
        "doctype": "Custom Field",
        "filters": [
            [
                "name",
                "in",
                [
                    "Item-vn_has_margin_price",
                    "Sales Invoice Item-vn_mrp",
                    "Sales Invoice Item-vn_valuation",
                ],
            ]
        ],
    },
    {
        "doctype": "Property Setter",
        "filters": [
            [
                "name",
                "in",
                [
                    "Customer-naming_series-options",
                    "Customer-customer_name-in_standard_filter",
                    "Supplier-naming_series-options",
                    "Supplier-supplier_name-in_standard_filter",
                    "Item-naming_series-options",
                    "Item-item_name-in_standard_filter",
                    "Item Price-uom-in_list_view",
                    "Item Price-min_qty-in_standard_filter",
                    "Item Price-min_qty-in_list_view",
                    "Item Price-price_list-in_list_view",
                    "Sales Invoice-naming_series-options",
                    "Sales Invoice-posting_date-in_list_view",
                    "Sales Invoice Item-qty-columns",
                    "Sales Invoice Item-rate-columns",
                    "Purchase Invoice-update_stock-default",
                    "Purchase Invoice-disable_rounded_total-default",
                ],
            ]
        ],
    },
]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/vn_custom/css/vn_custom.css"
app_include_js = ["vn_custom.bundle.js"]

# include js, css files in header of web template
# web_include_css = "/assets/vn_custom/css/vn_custom.css"
# web_include_js = "/assets/vn_custom/js/vn_custom.js"

# include js in page
page_js = {"point-of-sale": "public/includes/point_of_sale.js"}

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
# 	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "vn_custom.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "vn_custom.install.before_install"
# after_install = "vn_custom.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "vn_custom.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "Sales Invoice": {"on_update": "vn_custom.doc_events.sales_invoice.on_update"}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"vn_custom.tasks.all"
# 	],
# 	"daily": [
# 		"vn_custom.tasks.daily"
# 	],
# 	"hourly": [
# 		"vn_custom.tasks.hourly"
# 	],
# 	"weekly": [
# 		"vn_custom.tasks.weekly"
# 	]
# 	"monthly": [
# 		"vn_custom.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "vn_custom.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------

# override_whitelisted_methods = {
#     "method": "vn_custom.api.method"
# }

# Jinja Environment Customizations
# --------------------------------

# jenv = {"methods": ["get_mrp:vn_custom.utils.jinja.get_mrp"]}
