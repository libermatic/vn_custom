# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from vn_custom.doc_events.delivery_note import set_item_prices


def on_submit(doc, method):
    if doc.update_stock:
        set_item_prices(doc.items, doc.posting_date, doc.posting_time)


def on_cancel(doc, method):
    if doc.update_stock:
        set_item_prices(doc.items, doc.posting_date, doc.posting_time)
