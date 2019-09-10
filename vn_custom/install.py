# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe import _
from toolz import merge

documents = {
    "Price List": [
        {
            "price_list_name": "MRP",
            "currency": frappe.defaults.get_global_default("currency"),
            "enabled": 1,
            "selling": 1,
        }
    ]
}


settings = {
    "Selling Settings": {"cust_master_name": "Naming Series"},
    "Stock Settings": {"item_naming_by": "Naming Series", "show_barcode_field": 1},
    "VN Settings": {"mrp_price_list": "MRP"},
}


@frappe.whitelist()
def setup_defaults():
    if frappe.session.user != "Administrator":
        frappe.throw(_("Only allowed for Administrator"))
    _create_docs()
    _update_settings()


def _update_settings():
    def update(doctype, params):
        doc = frappe.get_single(doctype)
        doc.update(params)
        doc.save(ignore_permissions=True)

    for x in settings.items():
        update(*x)


def _create_docs():
    def insert(doctype, args):
        if not frappe.db.exists(doctype, args):
            frappe.get_doc(merge({"doctype": doctype}, args)).insert(
                ignore_permissions=True
            )

    for doctype, docs in documents.items():
        for doc in docs:
            insert(doctype, doc)
