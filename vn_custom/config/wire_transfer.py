# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from frappe import _


def get_data():
    return [
        {
            "label": _("Documents"),
            "items": [
                {
                    "type": "doctype",
                    "name": "Wire Transfer",
                    "description": _("Wire Transfer"),
                },
                {
                    "type": "doctype",
                    "name": "Wire Account",
                    "description": _("Wire Account"),
                },
            ],
        },
        {
            "label": _("Reports"),
            "items": [
                {
                    "type": "report",
                    "is_query_report": True,
                    "name": "Wire Transfer Summary",
                    "label": _("Wire Transfer Summary"),
                }
            ],
        },
        {
            "label": _("Settings"),
            "items": [
                {
                    "type": "doctype",
                    "name": "Wire Transfer Settings",
                    "description": _("Wire Transfer Settings"),
                }
            ],
        },
    ]
