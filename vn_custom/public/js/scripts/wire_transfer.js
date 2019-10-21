import pick from 'lodash/pick';

import { set_details, render_details } from './wire_account';

function set_total(frm) {
  const { amount = 0, fees = 0 } = frm.doc;
  frm.set_value('total', amount + fees);
}

async function set_default_fields(frm) {
  if (frm.doc.__islocal) {
    const {
      message: { mode_of_payment, bank_account } = {},
    } = await frappe.db.get_value('Wire Transfer Settings', null, [
      'mode_of_payment',
      'bank_account',
    ]);
    frm.set_value({ mode_of_payment, bank_account });
  }
}

function render_dashboard(frm) {
  if (!frm.doc.__islocal && frm.doc.docstatus < 2) {
    frm.dashboard.show();
    const $wrapper = $(
      '<div class="form-dashboard-section custom" />'
    ).appendTo(frm.dashboard.wrapper);
    frm.vue_details = render_details(
      frm,
      $wrapper.html('<div />').children()[0],
      true /* isExtended */
    );
    set_details(frm);
  }
}

function get_edge_date(comp_fn, dates) {
  return frappe.datetime.obj_to_str(
    new Date(
      comp_fn.apply(
        null,
        dates.filter(d => !!d).map(d => frappe.datetime.str_to_obj(d))
      )
    )
  );
}

function show_general_ledger(frm) {
  if (frm.doc.docstatus > 0) {
    frm.add_custom_button(__('New Wire Transfer'), function() {
      frappe.new_doc(
        'Wire Transfer',
        pick(frm.doc, ['account', 'sender_name', 'sender_mobile'])
      );
    });
  }
  if (frm.doc.docstatus === 1) {
    frm.add_custom_button(
      __('Accounting Ledger'),
      function() {
        const dates = [
          'request_datetime',
          'return_datetime',
          'transfer_datetime',
          'reverse_datetime',
        ].map(field => frm.doc[field]);
        frappe.route_options = {
          voucher_no: frm.doc.name,
          from_date: get_edge_date(Math.min, dates),
          to_date: get_edge_date(Math.max, dates),
          company: frm.doc.company,
          group_by: 'Group by Voucher (Consolidated)',
        };
        frappe.set_route('query-report', 'General Ledger');
      },
      __('View')
    );
  }
}

async function set_cash_account(frm) {
  const { mode_of_payment, company } = frm.doc;
  if (!mode_of_payment) {
    return frm.set_value('cash_account', null);
  }
  const { message: mop = {} } = await frappe.call({
    method:
      'erpnext.accounts.doctype.sales_invoice.sales_invoice.get_bank_cash_account',
    args: { mode_of_payment, company },
  });
  return frm.set_value('cash_account', mop.account);
}

export const bank_account_filters = { account_type: 'Bank', is_group: 0 };

const listview = {
  onload: function(lst) {
    lst.page.fields_dict.bank_account.get_query = function() {
      return { filters: bank_account_filters };
    };
  },
};

export default {
  listview,
  setup: function(frm) {
    frm.set_query('mode_of_payment', { enabled: 1 });
    frm.set_query('bank_account', bank_account_filters);
  },
  refresh: function(frm) {
    frm.toggle_enable(
      ['request_datetime', 'fees', 'mode_of_payment'],
      frm.doc.docstatus === 0 || frm.doc.status === 'Unpaid'
    );
    frm.toggle_enable(
      ['transfer_datetime', 'bank_account', 'bank_mode', 'transaction_id'],
      frm.doc.docstatus === 0 || frm.doc.status === 'Pending'
    );
    set_default_fields(frm);
    render_dashboard(frm);
    show_general_ledger(frm);
  },
  amount: async function(frm) {
    const { amount = 0 } = frm.doc;
    try {
      if (amount) {
        await frappe.call({ method: 'set_fees', doc: frm.doc });
        frm.refresh();
      }
    } finally {
      set_total(frm);
    }
  },
  fees: set_total,
  mode_of_payment: set_cash_account,
  before_workflow_action: function(frm) {
    frm.doc.workflow_action = frm.selected_workflow_action;
  },
  after_workflow_action: function(frm) {
    frm.reload_doc();
  },
};
