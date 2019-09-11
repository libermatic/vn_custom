# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
import frappe
from functools import partial
from toolz import compose, get, excepts, first


@frappe.whitelist()
def get_other_prices(item_code):
    def get_mrp(item_code):
        mrp_price_list = frappe.db.get_single_value("VN Settings", "mrp_price_list")
        return frappe.db.get_value(
            "Item Price",
            {"item_code": item_code, "price_list": mrp_price_list},
            "price_list_rate",
        )

    get_fifo_rate = compose(
        excepts(IndexError, partial(get, 1), lambda __: None),
        excepts(StopIteration, first, lambda __: []),
        excepts(TypeError, json.loads, lambda __: []),
        lambda x: frappe.db.get_value(
            "Stock Ledger Entry",
            {"item_code": x},
            "stock_queue",
            order_by="posting_date DESC, posting_time DESC, creation DESC",
        ),
    )

    return {"vn_mrp": get_mrp(item_code), "vn_valuation": get_fifo_rate(item_code)}
