# -*- coding: utf-8 -*-
# Copyright (c) 2019, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
import requests


class WireAccount(Document):
    def before_save(self):
        if self.ifsc:
            self.ifsc = self.ifsc.upper()
        if self.ifsc and (not self.bank or not self.branch):
            try:
                r = requests.get("https://ifsc.razorpay.com/{}".format(self.ifsc))
                r.raise_for_status()
                data = r.json()
                self.bank = self.bank or data.get("BANK")
                self.branch = self.branch or data.get("BRANCH")
            except requests.exceptions.HTTPError:
                frappe.throw(_("Invalid IFSC"))
