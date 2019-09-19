// Copyright (c) 2019, Libermatic and contributors
// For license information, please see license.txt

frappe.ui.form.on('Wire Transfer Settings', {
  setup: function(frm) {
    frm.set_query('cash_account', { account_type: 'Cash', is_group: 0 });
    frm.set_query('bank_account', { account_type: 'Bank', is_group: 0 });
    frm.set_query('transit_account', { root_type: 'Liability', is_group: 0 });
    frm.set_query('income_account', {
      account_type: 'Income Account',
      is_group: 0,
    });
    frm.set_query('cost_center', { is_group: 0 });
  },
});
