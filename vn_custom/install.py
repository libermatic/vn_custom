# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe import _
from toolz import merge

from vn_custom.utils import mapr


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
        "Party Type": [{"party_type": "Wire Account", "account_type": "Payable"}],
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


def workflows():
    return {
        "Wire Transfer Workflow": {
            "document_type": "Wire Transfer",
            "is_active": 1,
            "send_email_alert": 0,
            "workflow_state_field": "status",
            "states": [
                {
                    "state": "Draft",
                    "style": "Danger",
                    "doc_status": "0",
                    "allow_edit": "Accounts User",
                },
                {
                    "state": "Pending",
                    "style": "Primary",
                    "doc_status": "1",
                    "allow_edit": "Accounts User",
                },
                {
                    "state": "Unpaid",
                    "style": "Warning",
                    "doc_status": "1",
                    "allow_edit": "Accounts User",
                },
                {
                    "state": "Completed",
                    "style": "Success",
                    "doc_status": "1",
                    "allow_edit": "Accounts User",
                },
                {
                    "state": "Returned",
                    "style": "Info",
                    "doc_status": "1",
                    "allow_edit": "Accounts User",
                },
                {
                    "state": "Failed",
                    "style": "Danger",
                    "doc_status": "1",
                    "allow_edit": "Accounts User",
                    "is_optional_state": 1,
                },
                {
                    "state": "Cancelled",
                    "style": "Danger",
                    "doc_status": "2",
                    "allow_edit": "Accounts User",
                    "is_optional_state": 1,
                },
            ],
            "transitions": [
                {
                    "state": "Draft",
                    "action": "Accept",
                    "next_state": "Pending",
                    "allowed": "Accounts User",
                    "allow_self_approval": 1,
                },
                {
                    "state": "Draft",
                    "action": "Transfer",
                    "next_state": "Unpaid",
                    "allowed": "Accounts User",
                    "allow_self_approval": 1,
                },
                {
                    "state": "Pending",
                    "action": "Cancel",
                    "next_state": "Cancelled",
                    "allowed": "Accounts User",
                    "allow_self_approval": 1,
                },
                {
                    "state": "Pending",
                    "action": "Transfer",
                    "next_state": "Completed",
                    "allowed": "Accounts User",
                    "allow_self_approval": 1,
                },
                {
                    "state": "Pending",
                    "action": "Return",
                    "next_state": "Returned",
                    "allowed": "Accounts User",
                    "allow_self_approval": 1,
                },
                {
                    "state": "Unpaid",
                    "action": "Cancel",
                    "next_state": "Cancelled",
                    "allowed": "Accounts User",
                    "allow_self_approval": 1,
                },
                {
                    "state": "Unpaid",
                    "action": "Accept",
                    "next_state": "Completed",
                    "allowed": "Accounts User",
                    "allow_self_approval": 1,
                },
                {
                    "state": "Unpaid",
                    "action": "Reverse",
                    "next_state": "Failed",
                    "allowed": "Accounts User",
                    "allow_self_approval": 1,
                },
                {
                    "state": "Completed",
                    "action": "Reverse",
                    "next_state": "Failed",
                    "allowed": "Accounts User",
                    "allow_self_approval": 1,
                },
                {
                    "state": "Failed",
                    "action": "Return",
                    "next_state": "Returned",
                    "allowed": "Accounts User",
                    "allow_self_approval": 1,
                },
                {
                    "state": "Completed",
                    "action": "Cancel",
                    "next_state": "Cancelled",
                    "allowed": "Accounts User",
                    "allow_self_approval": 1,
                },
            ],
        }
    }


@frappe.whitelist()
def setup_defaults():
    if frappe.session.user != "Administrator":
        frappe.throw(_("Only allowed for Administrator"))
    _create_docs()
    _update_settings()
    _setup_workflow()


def _update_settings():
    def update(doctype, params):
        doc = frappe.get_single(doctype)
        doc.update(params)
        doc.save(ignore_permissions=True)

    mapr(lambda x: update(*x), settings().items())


def _create_docs():
    def insert_or_update(doctype, args):
        docname = frappe.db.exists(doctype, args)
        if not docname:
            frappe.get_doc(merge({"doctype": doctype}, args)).insert(
                ignore_permissions=True
            )
        else:
            doc = frappe.get_doc(doctype, docname)
            doc.update(args)
            doc.save(ignore_permissions=True)

    for doctype, docs in documents().items():
        mapr(lambda x: insert_or_update(doctype, x), docs)


def _setup_workflow():
    def make_action(name):
        if not frappe.db.exists("Workflow Action Master", name):
            frappe.get_doc(
                {"doctype": "Workflow Action Master", "workflow_action_name": name}
            ).insert(ignore_permissions=True)

    def make_state(name, style=None):
        if not frappe.db.exists("Workflow State", name):
            frappe.get_doc(
                {
                    "doctype": "Workflow State",
                    "workflow_state_name": name,
                    "style": style,
                }
            ).insert(ignore_permissions=True)
        else:
            doc = frappe.get_doc("Workflow State", name)
            doc.update({"style": style})
            doc.save(ignore_permissions=True)

    def make_role(name, desk_access=1):
        if not frappe.db.exists("Role", name):
            frappe.get_doc(
                {"doctype": "Role", "role_name": name, "desk_access": desk_access}
            ).insert(ignore_permissions=True)

    def make_workflow(name, args):
        if args.get("transitions"):
            mapr(lambda x: make_action(x.get("action")), args.get("transitions"))

        if args.get("states"):
            mapr(
                lambda x: make_state(x.get("state"), x.get("style")), args.get("states")
            )
            mapr(lambda x: make_role(x.get("allow_edit")), args.get("states"))

        if not frappe.db.exists("Workflow", name):
            frappe.get_doc(
                merge({"doctype": "Workflow", "workflow_name": name}, args)
            ).insert(ignore_permissions=True)
        else:
            doc = frappe.get_doc("Workflow", name)
            doc.update(args)
            doc.save(ignore_permissions=True)

    mapr(lambda x: make_workflow(*x), workflows().items())
