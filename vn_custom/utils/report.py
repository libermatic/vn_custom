from frappe import _
from toolz import compose, concatv


def make_column(key, label=None, type="Data", options=None, width=120, hidden=0):
    return {
        "label": _(label or key.replace("_", " ").title()),
        "fieldname": key,
        "fieldtype": type,
        "options": options,
        "width": width,
        "hidden": hidden,
    }


join_clauses = compose(lambda x: " AND ".join(x), concatv)
