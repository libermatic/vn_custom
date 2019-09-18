# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from toolz import excepts, first, compose


@frappe.whitelist()
def get_default_accounts():
    get_bank_account = compose(
        lambda x: x.bank_account,
        excepts(StopIteration, first, lambda __: frappe._dict()),
    )
    settings = frappe.get_single("Wire Transfer Settings")
    print(get_bank_account(settings.bank_accounts))
    return {
        "cash_account": settings.cash_account,
        "bank_account": get_bank_account(settings.bank_accounts),
    }
