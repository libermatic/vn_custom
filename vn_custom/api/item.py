# -*- coding: utf-8 -*-
import json
import frappe
from functools import partial
from toolz import compose, get, excepts, first
from erpnext.stock.get_item_details import get_conversion_factor


@frappe.whitelist()
def get_other_prices(item_code, uom=None):
    def get_mrp(item_code):
        mrp_price_list = frappe.db.get_single_value("VN Settings", "mrp_price_list")
        return (
            frappe.db.get_value(
                "Item Price",
                {"item_code": item_code, "price_list": mrp_price_list},
                "price_list_rate",
            )
            or 0
        )

    get_fifo_rate = compose(
        excepts(IndexError, partial(get, 1), lambda __: 0),
        excepts(StopIteration, first, lambda __: []),
        excepts(TypeError, json.loads, lambda __: []),
        lambda x: frappe.db.get_value(
            "Stock Ledger Entry",
            {"item_code": x},
            "stock_queue",
            order_by="posting_date DESC, posting_time DESC, creation DESC",
        ),
    )
    get_cf = compose(
        partial(get, "conversion_factor"),
        lambda x: get_conversion_factor(
            x, uom or frappe.db.get_value("Item", x, "stock_uom")
        ),
    )

    conversion_factor = get_cf(item_code)
    return {
        "vn_mrp": conversion_factor * get_mrp(item_code),
        "vn_valuation": conversion_factor * get_fifo_rate(item_code),
    }
