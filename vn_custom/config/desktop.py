# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from frappe import _


def get_data():
    return [
        {
            "module_name": "Wire Transfer",
            "category": "Modules",
            "label": _("Wire Transfer"),
            "color": "grey",
            "icon": "octicon octicon-file-directory",
            "type": "module",
            "description": "Wire Transfer",
        }
    ]
