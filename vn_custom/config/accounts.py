# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from frappe import _


def get_data():
    return [
        {
            "label": _("General Ledger"),
            "items": [
                {
                    "type": "report",
                    "is_query_report": True,
                    "name": "Cash Ledger",
                    "label": "Cash Ledger",
                },
            ],
        },
    ]
