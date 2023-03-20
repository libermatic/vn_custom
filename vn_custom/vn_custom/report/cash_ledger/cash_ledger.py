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
    return "", frappe._dict(values)


def _get_data(clauses, values, keys):
    GLEntry = frappe.qb.DocType("GL Entry")
    gles = (
        frappe.qb.from_(GLEntry)
        .select(
            GLEntry.posting_date,
            GLEntry.voucher_type,
            GLEntry.voucher_no,
            GLEntry.debit,
            GLEntry.credit,
        )
        .where(
            (GLEntry.account == values.cash_account)
            & (GLEntry.posting_date[values.from_date : values.to_date])
        )
        .orderby(GLEntry.posting_date)
    ).run(as_dict=1)

    purchase_vouchers = [
        x.voucher_no for x in gles if x.voucher_type == "Purchase Invoice"
    ]
    payment_vouchers = [x.voucher_no for x in gles if x.voucher_type == "Payment Entry"]
    other_vouchers = [
        x.voucher_no
        for x in gles
        if x.voucher_type not in ["Purchase Invoice", "Payment Entry"]
    ]

    PurchaseInvoiceItem = frappe.qb.DocType("Purchase Invoice Item")
    pi_cost_centers = (
        (
            frappe.qb.from_(PurchaseInvoiceItem)
            .select(
                PurchaseInvoiceItem.parent.as_("voucher_no"),
                PurchaseInvoiceItem.cost_center,
            )
            .where(PurchaseInvoiceItem.parent.isin(purchase_vouchers))
        ).run(as_dict=1)
        if purchase_vouchers
        else []
    )
    PaymentEntryReference = frappe.qb.DocType("Payment Entry Reference")
    SalesInvoiceItem = frappe.qb.DocType("Sales Invoice Item")
    invoice_sub = (
        frappe.qb.from_(SalesInvoiceItem)
        .select(SalesInvoiceItem.parent, SalesInvoiceItem.cost_center)
        .union_all(
            frappe.qb.from_(PurchaseInvoiceItem).select(
                PurchaseInvoiceItem.parent, PurchaseInvoiceItem.cost_center
            )
        )
        .as_("invoice_sub")
    )
    pe_cost_centers = (
        (
            frappe.qb.from_(PaymentEntryReference)
            .left_join(invoice_sub)
            .on(invoice_sub.parent == PaymentEntryReference.reference_name)
            .where(
                (PaymentEntryReference.docstatus == 1)
                & (PaymentEntryReference.parent.isin(payment_vouchers))
            )
            .select(
                PaymentEntryReference.parent.as_("voucher_no"), invoice_sub.cost_center
            )
        ).run(as_dict=1)
        if payment_vouchers
        else []
    )

    Account = frappe.qb.DocType("Account")
    other_cost_centers = (
        (
            frappe.qb.from_(GLEntry)
            .left_join(Account)
            .on(Account.name == GLEntry.account)
            .where(
                (Account.root_type.isin(["Income", "Expense"]))
                & (GLEntry.voucher_no.isin(other_vouchers))
            )
            .select(GLEntry.voucher_no, GLEntry.cost_center)
        ).run(as_dict=1)
        if other_vouchers
        else [],
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
