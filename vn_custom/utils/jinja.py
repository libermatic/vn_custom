# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe


def get_mrp(item_code):
    mrp_price_list = frappe.db.get_single_value("VN Settings", "mrp_price_list")
    return frappe.db.get_value(
        "Item Price",
        {"item_code": item_code, "price_list": mrp_price_list},
        "price_list_rate",
    )
