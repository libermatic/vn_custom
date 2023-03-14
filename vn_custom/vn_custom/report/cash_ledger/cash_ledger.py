# Copyright (c) 2013, Libermatic and contributors
# For license information, please see license.txt

import frappe
from functools import partial
from toolz import compose, pluck, merge, groupby, first, excepts

from vn_custom.utils import pick
from vn_custom.utils.report import make_column


def execute(filters=None):
    columns = _get_columns(filters)
    keys = compose(list, partial(pluck, "fieldname"))(columns)
    clauses, values = _get_filters(filters)
    data = _get_data(clauses, values, keys)
    return columns, data


def _get_columns(filters):
    return [
        make_column("posting_date", type="Date", width=90),
        make_column("voucher_type"),
        make_column("voucher_no", type="Dynamic Link", width=150),
        make_column("debit", type="Currency"),
        make_column("credit", type="Currency"),
        make_column("cost_center"),
    ]


def _get_filters(filters):
    values = merge(
        filters,
        {"from_date": filters.date_range[0], "end_date": filters.date_range[1]}
        if filters.date_range
        else {},
    )
    return "", values


def _get_data(clauses, values, keys):
    gles = frappe.db.sql(
        """
            SELECT
                gle.posting_date AS posting_date,
                gle.voucher_type AS voucher_type,
                gle.voucher_no AS voucher_no,
                gle.debit AS debit,
                gle.credit AS credit
            FROM `tabGL Entry` AS gle
            WHERE
                gle.account = %(cash_account)s AND
                gle.posting_date BETWEEN %(from_date)s AND %(end_date)s
            ORDER BY gle.posting_date
        """.format(
            clauses=clauses
        ),
        values=values,
        as_dict=1,
    )

    purchase_vouchers = [
        x.voucher_no for x in gles if x.voucher_type == "Purchase Invoice"
    ]
    payment_vouchers = [x.voucher_no for x in gles if x.voucher_type == "Payment Entry"]
    other_vouchers = [
        x.voucher_no
        for x in gles
        if x.voucher_type not in ["Purchase Invoice", "Payment Entry"]
    ]

    pi_cost_centers = (
        frappe.db.sql(
            """
            SELECT
                pii.parent AS voucher_no,
                pii.cost_center AS cost_center
            FROM `tabPurchase Invoice Item` AS pii
            WHERE pii.parent IN %(voucher_nos)s
        """,
            values={"voucher_nos": purchase_vouchers},
            as_dict=1,
        )
        if purchase_vouchers
        else []
    )
    pe_cost_centers = (
        frappe.db.sql(
            """
            SELECT
                per.parent AS voucher_no,
                ii.cost_center AS cost_center
            FROM `tabPayment Entry Reference` AS per
            LEFT JOIN `tabPayment Entry` AS pe ON pe.name = per.parent
            LEFT JOIN (
                SELECT parent, cost_center FROM `tabSales Invoice Item`
                UNION ALL
                SELECT parent, cost_center FROM `tabPurchase Invoice Item`
            ) AS ii
                ON ii.parent = per.reference_name
            WHERE
                pe.docstatus = 1 AND per.parent IN %(voucher_nos)s
        """,
            values={"voucher_nos": payment_vouchers},
            as_dict=1,
        )
        if payment_vouchers
        else []
    )

    other_cost_centers = (
        frappe.db.sql(
            """
            SELECT
                gle.voucher_no AS voucher_no,
                gle.cost_center AS cost_center
            FROM `tabGL Entry` AS gle
            LEFT JOIN `tabAccount` AS a ON
                a.name = gle.account
            WHERE
                a.root_type IN ('Income', 'Expense') AND
                gle.voucher_no IN %(voucher_nos)s
        """,
            values={
                "voucher_nos": [
                    x.voucher_no
                    for x in gles
                    if x.voucher_type not in ["Purchase Invoice", "Payment Entry"]
                ]
            },
            as_dict=1,
        )
        if other_vouchers
        else []
    )

    def filter_cost_center(result):
        cost_center = values.get("cost_center")
        if cost_center:
            return [x for x in result if x.get("cost_center") == cost_center]
        return result

    make_row = compose(
        partial(pick, keys),
        _set_cost_center(pi_cost_centers, pe_cost_centers, other_cost_centers),
    )
    return filter_cost_center([make_row(x) for x in gles])


def _set_cost_center(pi_cost_centers, pe_cost_centers, other_cost_centers):
    pi_grouped = groupby("voucher_no", pi_cost_centers)
    pe_grouped = groupby("voucher_no", pe_cost_centers)
    other_grouped = groupby("voucher_no", other_cost_centers)

    def get_grouped(x):
        doctype = x.get("voucher_type")
        if doctype == "Purchase Invoice":
            return pi_grouped
        if doctype == "Payment Entry":
            return pe_grouped
        return other_grouped

    def get_cc(grouped):
        return compose(
            excepts(StopIteration, first, lambda _: {}),
            lambda x: grouped.get(x, []),
            lambda x: x.get("voucher_no"),
        )

    def fn(row):
        cc = get_cc(get_grouped(row))
        return merge(row, cc(row))

    return fn
