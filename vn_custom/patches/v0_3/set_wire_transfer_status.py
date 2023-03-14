# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

import frappe
from functools import partial
from toolz import compose, pluck


def execute():
    for name in _get_names("Wire Transfer"):
        workflow_state = frappe.db.get_value("Wire Transfer", name, "workflow_state")
        frappe.db.set_value("Wire Transfer", name, "status", workflow_state)


_get_names = compose(partial(pluck, "name"), frappe.get_all)
