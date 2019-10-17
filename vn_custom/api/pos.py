# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from functools import partial
from toolz import compose, pluck, get, concatv, reduceby, merge


@frappe.whitelist()
def get_items(
    start, page_length, price_list, item_group, search_value="", pos_profile=None
):
    from erpnext.selling.page.point_of_sale.point_of_sale import get_items

    result = get_items(
        start, page_length, price_list, item_group, search_value, pos_profile
    )

    get_item_codes = compose(
        list, partial(pluck, "item_code"), partial(get, "items", default=[])
    )
    make_clauses = compose(lambda x: " AND ".join(x), concatv)
    get_qtys_by_item_code = compose(
        partial(reduceby, "item_code", lambda a, x: merge(a, x), init={}), frappe.db.sql
    )

    warehouse = (
        frappe.db.get_value("POS Profile", pos_profile, "warehouse")
        if pos_profile
        else None
    )

    qtys = get_qtys_by_item_code(
        """
            SELECT item_code, SUM(actual_qty) AS actual_qty, stock_uom
            FROM `tabBin`
            WHERE {clauses}
            GROUP BY item_code
        """.format(
            clauses=make_clauses(
                ["item_code IN %(item_codes)s"],
                ["warehouse=%(warehouse)s"] if warehouse else [],
            )
        ),
        values={"warehouse": warehouse, "item_codes": get_item_codes(result)},
        as_dict=1,
    )
    return merge(
        result,
        {
            "items": list(
                map(
                    lambda x: merge(x, get(x["item_code"], qtys, {})),
                    get("items", result, []),
                )
            )
        },
    )
