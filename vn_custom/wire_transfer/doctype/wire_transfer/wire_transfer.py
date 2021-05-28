# -*- coding: utf-8 -*-
# Copyright (c) 2019, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import get_datetime, getdate, flt
from frappe.workflow.doctype.workflow_action.workflow_action import (
    process_workflow_actions,
)
from erpnext.controllers.accounts_controller import AccountsController
from erpnext.accounts.general_ledger import make_gl_entries, make_reverse_gl_entries
from erpnext.accounts.utils import get_account_currency
from erpnext.accounts.doctype.sales_invoice.sales_invoice import get_bank_cash_account
from toolz import merge

from vn_custom.utils import mapr


ACCEPT = "Accept"
RETURN = "Return"
TRANSFER = "Transfer"
REVERSE = "Reverse"


class WireTransfer(AccountsController):
    def validate(self):
        pass

    def before_save(self):
        self.status = self.workflow_state
        mop = get_bank_cash_account(self.mode_of_payment, self.company) or {}
        self.cash_account = mop.get("account")

    def before_submit(self):
        self._set_missing_fields()

    def on_submit(self):
        self.make_gl_entry()

    def before_update_after_submit(self):
        self.flags.ignore_validate_update_after_submit = True
        self._set_missing_fields()

    def on_update_after_submit(self):
        process_workflow_actions(self, "on_update_after_submit")
        self.make_gl_entry()

    def on_cancel(self):
        self.ignore_linked_doctypes = "GL Entry"
        self.make_gl_entry()

    def make_gl_entry(self):
        if self.docstatus == 2:
            return make_reverse_gl_entries(
                voucher_type=self.doctype, voucher_no=self.name
            )

        settings = frappe.get_single("Wire Transfer Settings")
        sign = -1 if self.workflow_action in [RETURN, REVERSE] else 1
        if self.workflow_action in [ACCEPT, RETURN]:
            make_gl_entries(
                mapr(
                    self.get_gl_dict,
                    [
                        {
                            "account": self.cash_account,
                            "against": self.account,
                            "debit": self.total * sign,
                        },
                        {
                            "account": settings.income_account,
                            "against": self.account,
                            "credit": self.fees * sign,
                            "cost_center": settings.cost_center,
                        },
                        {
                            "account": settings.transit_account,
                            "party": self.account,
                            "credit": self.amount * sign,
                        },
                    ],
                )
            )
        elif self.workflow_action in [TRANSFER, REVERSE]:
            make_gl_entries(
                mapr(
                    self.get_gl_dict,
                    [
                        {
                            "account": self.bank_account,
                            "against": self.account,
                            "credit": self.amount * sign,
                            "remarks": self._get_remarks(),
                        },
                        {
                            "account": settings.transit_account,
                            "against": self.bank_account,
                            "debit": self.amount * sign,
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

    def _set_missing_fields(self):
        if not self.get("workflow_action"):
            self.workflow_action = None
        self.total = flt(self.amount) + flt(self.fees)
        if self.workflow_action == ACCEPT and not self.request_datetime:
            self.request_datetime = get_datetime()
        elif self.workflow_action == RETURN and not self.return_datetime:
            self.return_datetime = get_datetime()
        elif self.workflow_action == TRANSFER and not self.transfer_datetime:
            self.transfer_datetime = get_datetime()
        elif self.workflow_action == REVERSE and not self.reverse_datetime:
            self.reverse_datetime = get_datetime()

    def _get_posting_date(self):
        if self.workflow_action == ACCEPT:
            return getdate(self.request_datetime)
        elif self.workflow_action == RETURN:
            return getdate(self.return_datetime)
        elif self.workflow_action == TRANSFER:
            return getdate(self.transfer_datetime)
        elif self.workflow_action == REVERSE:
            return getdate(self.reverse_datetime)

    def _get_remarks(self):
        if self.workflow_action == TRANSFER and self.transaction_id:
            return "Transaction reference no {} dated {}".format(
                self.transaction_id, getdate(self.transfer_datetime)
            )
        return None

    @frappe.whitelist()
    def set_fees(self):
        settings = frappe.get_single("Wire Transfer Settings")
        for rule in settings.fees_rules:
            eval_globals = {"ceil": frappe.utils.ceil}
            eval_locals = self.as_dict()
            if not rule.condition or frappe.safe_eval(
                rule.condition, eval_locals=eval_locals
            ):
                self.fees = frappe.safe_eval(
                    rule.formula, eval_globals=eval_globals, eval_locals=eval_locals
                )
                return self.fees
        self.fees = 0
        return self.fees
