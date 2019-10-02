import { set_details, render_details } from './wire_account';

function set_total(frm) {
  const { amount = 0, fees = 0 } = frm.doc;
  frm.set_value('total', amount + fees);
}

async function set_default_fields(frm) {
  if (frm.doc.__islocal) {
    const {
      message: { cash_account, bank_account } = {},
    } = await frappe.db.get_value('Wire Transfer Settings', null, [
      'cash_account',
      'bank_account',
    ]);
    frm.set_value({ cash_account, bank_account });
  }
}

function render_dashboard(frm) {
  if (frm.doc.docstatus > 0) {
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

export default {
  setup: function(frm) {
    frm.set_query('cash_account', {
      account_type: ['in', ['Cash', 'Bank']],
      is_group: 0,
    });
    frm.set_query('bank_account', { account_type: 'Bank', is_group: 0 });
  },
  refresh: function(frm) {
    frm.toggle_enable(
      ['request_datetime', 'fees', 'cash_account'],
      frm.doc.docstatus === 0 || frm.doc.workflow_state === 'Unpaid'
    );
    frm.toggle_enable(
      ['transfer_datetime', 'bank_account', 'transaction_id'],
      frm.doc.docstatus === 0 || frm.doc.workflow_state === 'Pending'
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
  before_workflow_action: function(frm) {
    frm.doc.workflow_action = frm.selected_workflow_action;
  },
  after_workflow_action: function(frm) {
    frm.reload_doc();
  },
};
