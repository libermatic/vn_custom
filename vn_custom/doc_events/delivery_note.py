# -*- coding: utf-8 -*-
import frappe
import json
from functools import partial
from toolz import compose, first, get, excepts
from erpnext.stock.stock_ledger import get_previous_sle
from frappe.query_builder.functions import IfNull


def on_submit(doc, method):
    set_item_prices(doc.items, doc.posting_date, doc.posting_time)


def on_cancel(doc, method):
    set_item_prices(doc.items, doc.posting_date, doc.posting_time)


def set_item_prices(items, posting_date, posting_time):
    get_rate = compose(
        excepts(IndexError, partial(get, 1), lambda __: None),
        excepts(StopIteration, first, lambda __: []),
        excepts(TypeError, json.loads, lambda __: []),
        lambda x: x.stock_queue,
        lambda x: get_previous_sle(
            {"item_code": x, "posting_date": posting_date, "posting_time": posting_time}
        ),
    )
    selling_price_list = frappe.db.get_single_value(
        "Selling Settings", "selling_price_list"
    )

    def get_price(item_code):
        get_first = compose(
            partial(get, "name"), excepts(StopIteration, first, lambda __: {})
        )
        ItemPrice = frappe.qb.DocType("Item Price")
        prices = (
            frappe.qb.from_(ItemPrice)
            .select(ItemPrice.name)
            .where(
                (ItemPrice.item_code == item_code)
                & (ItemPrice.price_list == selling_price_list)
                & (IfNull(ItemPrice.uom, "") == "")
            )
        ).run(as_dict=1)
        if len(prices) > 1:
            frappe.throw(
                frappe._(
                    "Cannot set {} Item Price because multiple prices exists"
                ).format(selling_price_list)
            )
        item_price = get_first(prices)
        return frappe.get_doc("Item Price", item_price) if item_price else None

    def has_margin_price(item_code):
        return frappe.db.get_value("Item", item_code, "vn_has_margin_price")

    for item in items:
        if has_margin_price(item.item_code):
            rate = get_rate(item.item_code)
            if rate:
                item_price = get_price(item.item_code)
                if item_price and item_price.price_list_rate != rate:
                    item_price.price_list_rate = rate
                    item_price.save()
