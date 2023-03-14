import frappe
from frappe import _
from functools import partial
from toolz import compose, pluck, concatv, merge

from vn_custom.utils import pick, mapr


def execute(filters):
    columns = _get_columns(filters)
    keys = compose(list, partial(pluck, "fieldname"))(columns)
    clauses, values = _get_filters(filters)
    data = _get_data(clauses, values, keys)
    return columns, data


def _get_columns(filters):
    def make_column(key, label=None, type="Data", options=None, width=90):
        return {
            "label": _(label or key.replace("_", " ").title()),
            "fieldname": key,
            "fieldtype": type,
            "options": options,
            "width": width,
        }

    return [
        make_column("wire_transfer", type="Link", options="Wire Transfer", width=120),
        make_column("account", type="Link", options="Wire Account", width=120),
        make_column("account_holder", width=150),
        make_column("status"),
        make_column("request_datetime", type="Datetime"),
        make_column("transfer_datetime", type="Datetime"),
        make_column("amount", type="Currency", width=120),
        make_column("fees", type="Currency", width=120),
        make_column("total", type="Currency", width=120),
    ]


def _get_filters(filters):
    date_field_map = {
        "Accepted": "request_datetime",
        "Transfered": "transfer_datetime",
        "Returned": "return_datetime",
        "Failed": "reverse_datetime",
        "Created": "creation",
        "Modified": "modified",
    }
    clauses = concatv(
        [
            "docstatus = 1",
            "DATE({date_field}) BETWEEN %(from_date)s AND %(to_date)s".format(
                date_field=date_field_map.get(filters.date_type, "creation")
            ),
        ],
        ["bank_account = %(bank_account)s"] if filters.bank_account else [],
        ["bank_mode = %(bank_mode)s"] if filters.bank_mode else [],
    )

    values = merge(
        pick(["bank_account", "bank_mode"], filters),
        {"from_date": filters.date_range[0], "to_date": filters.date_range[1]},
    )
    return " AND ".join(clauses), values


def _get_data(clauses, values, keys):
    rows = frappe.db.sql(
        """
            SELECT
                name AS wire_transfer,
                account,
                account_holder,
                status,
                request_datetime,
                transfer_datetime,
                amount,
                fees,
                total
            FROM `tabWire Transfer`
            WHERE {clauses}
        """.format(
            clauses=clauses
        ),
        values=values,
        as_dict=1,
    )

    make_row = partial(pick, keys)
    return mapr(make_row, rows)
