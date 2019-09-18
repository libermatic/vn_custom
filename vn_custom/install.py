# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe import _
from toolz import merge


def documents():
    return {
        "Price List": [
            {
                "price_list_name": "MRP",
                "currency": frappe.defaults.get_global_default("currency"),
                "enabled": 1,
                "selling": 1,
            }
        ],
        "Account": [
            {
                "is_group": 0,
                "company": frappe.defaults.get_global_default("company"),
                "account_name": "Transfer Transit",
                "parent_account": frappe.db.exists(
                    "Account",
                    {
                        "company": frappe.defaults.get_global_default("company"),
                        "account_name": "Accounts Payable",
                    },
                ),
            }
        ],
    }


def settings():
    return {
        "Buying Settings": {"supp_master_name": "Naming Series"},
        "Selling Settings": {"cust_master_name": "Naming Series"},
        "Stock Settings": {"item_naming_by": "Naming Series", "show_barcode_field": 1},
        "VN Settings": {"mrp_price_list": "MRP"},
        "Wire Transfer Settings": {
            "transit_account": frappe.db.exists(
                "Account", {"account_name": "Transfer Transit"}
            )
        },
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

    for x in settings().items():
        update(*x)


def _create_docs():
    def insert(doctype, args):
        if not frappe.db.exists(doctype, args):
            frappe.get_doc(merge({"doctype": doctype}, args)).insert(
                ignore_permissions=True
            )

    for doctype, docs in documents().items():
        for doc in docs:
            insert(doctype, doc)
