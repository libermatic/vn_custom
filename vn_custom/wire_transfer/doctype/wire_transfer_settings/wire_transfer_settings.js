// Copyright (c) 2019, Libermatic and contributors
// For license information, please see license.txt

frappe.ui.form.on('Wire Transfer Settings', {
  setup: function(frm) {
    frm.set_query('cash_account', { account_type: 'Cash', is_group: 0 });
  },
});
