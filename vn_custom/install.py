# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe import _


settings = {
    "Selling Settings": {"cust_master_name": "Naming Series"},
    "Stock Settings": {"item_naming_by": "Naming Series", "show_barcode_field": 1},
}


@frappe.whitelist()
def setup_defaults():
    if frappe.session.user != "Administrator":
        frappe.throw(_("Only allowed for Administrator"))
    _update_settings()


def _update_settings():
    def update(doctype, params):
        doc = frappe.get_single(doctype)
        doc.update(params)
        doc.save(ignore_permissions=True)

    for x in settings.items():
        update(*x)
