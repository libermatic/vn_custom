# -*- coding: utf-8 -*-
from vn_custom.doc_events.delivery_note import set_item_prices
from vn_custom.api.item import get_other_prices
from vn_custom.utils import pick


def on_update(doc, method):
    for item in doc.items:
        if not item.vn_mrp or not item.vn_valuation:
            prices = get_other_prices(item.item_code, item.uom)
            item.update(pick(["vn_mrp", "vn_valuation"], prices))


def on_submit(doc, method):
    if doc.update_stock:
        set_item_prices(doc.items, doc.posting_date, doc.posting_time)


def on_cancel(doc, method):
    if doc.update_stock:
        set_item_prices(doc.items, doc.posting_date, doc.posting_time)
