# -*- coding: utf-8 -*-
# Copyright (c) 2019, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import get_datetime, getdate, flt
from erpnext.controllers.accounts_controller import AccountsController
from erpnext.accounts.general_ledger import make_gl_entries, delete_gl_entries
from erpnext.accounts.utils import get_account_currency
from toolz import merge

from vn_custom.utils import mapr


class WireTransfer(AccountsController):
    def validate(self):
        if (
            self.request_datetime
            and self.transfer_datetime
            and get_datetime(self.request_datetime)
            > get_datetime(self.transfer_datetime)
        ):
            frappe.throw(_("Request Datetime cannot be after Transfer Datetime"))

    def before_submit(self):
        self.total = flt(self.amount) + flt(self.fees)
        if not self.request_datetime:
            self.request_datetime = get_datetime()

    def on_submit(self):
        self.make_gl_entry()

    def before_update_after_submit(self):
        if self.workflow_state == "Completed" and not self.transfer_datetime:
            self.transfer_datetime = get_datetime()

    def on_update_after_submit(self):
        self.make_gl_entry()

    def on_cancel(self):
        delete_gl_entries(voucher_type=self.doctype, voucher_no=self.name)

    def make_gl_entry(self):
        settings = frappe.get_single("Wire Transfer Settings")
        if self.workflow_state == "Pending":
            make_gl_entries(
                mapr(
                    self.get_gl_dict,
                    [
                        {
                            "account": self.cash_account,
                            "against": self.account_holder,
                            "debit": self.total,
                        },
                        {
                            "account": settings.income_account,
                            "against": self.account,
                            "credit": self.fees,
                            "cost_center": settings.cost_center,
                        },
                        {
                            "account": settings.transit_account,
                            "party": self.account,
                            "credit": self.amount,
                        },
                    ],
                )
            )
        elif self.workflow_state == "Completed":
            remarks = (
                "Transaction reference no {} dated {}".format(
                    self.transaction_id, getdate(self.transfer_datetime)
                )
                if self.transaction_id
                else None
            )
            make_gl_entries(
                mapr(
                    self.get_gl_dict,
                    [
                        {
                            "account": self.bank_account,
                            "party": self.account,
                            "against": settings.transit_account,
                            "credit": self.amount,
                            "remarks": remarks,
                        },
                        {
                            "account": settings.transit_account,
                            "against": self.bank_account,
                            "debit": self.amount,
                        },
                    ],
                )
            )

    def get_gl_dict(self, args):
        account = args.get("account")
        party = args.get("party")
        return super(WireTransfer, self).get_gl_dict(
            merge(
                args,
                {
                    "posting_date": self._get_posting_date(),
                    "account_currency": get_account_currency(account),
                    "party_type": "Wire Account" if party else None,
                },
            )
        )

    def _get_posting_date(self):
        if self.workflow_state == "Pending":
            return getdate(self.request_datetime)
        elif self.workflow_state == "Completed":
            return getdate(self.transfer_datetime)
