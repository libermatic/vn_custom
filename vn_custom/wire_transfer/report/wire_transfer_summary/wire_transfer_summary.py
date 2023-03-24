import frappe
from frappe import _


def execute(filters):
    return _get_columns(filters), _get_data(filters)


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


def _get_data(filters):
    date_field_map = {
        "Accepted": "request_datetime",
        "Transfered": "transfer_datetime",
        "Returned": "return_datetime",
        "Failed": "reverse_datetime",
        "Created": "creation",
        "Modified": "modified",
    }
    WireTransfer = frappe.qb.DocType("Wire Transfer")
    q = (
        frappe.qb.from_(WireTransfer)
        .where(
            (WireTransfer.docstatus == 1)
            & (
                frappe.query_builder.functions.Date(
                    WireTransfer[date_field_map.get(filters.date_type, "creation")]
                )[filters.date_range[0] : filters.date_range[1]]
            )
        )
        .select(
            WireTransfer.name.as_("wire_transfer"),
            WireTransfer.account,
            WireTransfer.account_holder,
            WireTransfer.status,
            WireTransfer.request_datetime,
            WireTransfer.transfer_datetime,
            WireTransfer.amount,
            WireTransfer.fees,
            WireTransfer.total,
        )
    )

    if filters.bank_mode:
        q.where(WireTransfer.bank_mode == filters.bank_mode)
    if filters.bank_account:
        q.where(WireTransfer.bank_account == filters.bank_account)

    return q.run(as_dict=1)