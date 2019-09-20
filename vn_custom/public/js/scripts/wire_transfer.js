function set_total(frm) {
  const { amount = 0, fees = 0 } = frm.doc;
  frm.set_value('total', amount + fees);
}

async function set_default_fields(frm) {
  if (frm.doc.__islocal) {
    frm.set_value('request_datetime', frappe.datetime.now_datetime());
    const {
      message: { cash_account, bank_account } = {},
    } = await frappe.db.get_value('Wire Transfer Settings', null, [
      'cash_account',
      'bank_account',
    ]);
    frm.set_value({ cash_account, bank_account });
  }
}

export default {
  refresh: function(frm) {
    frm.toggle_reqd('request_datetime', frm.doc.docstatus < 1);
    frm.toggle_enable(
      ['transfer_datetime', 'bank_account', 'transaction_id'],
      frm.doc.workflow_state !== 'Completed'
    );
    frm.set_query('cash_account', { account_type: 'Cash', is_group: 0 });
    frm.set_query('bank_account', { account_type: 'Bank', is_group: 0 });
    set_default_fields(frm);
  },
  amount: set_total,
  fees: set_total,
  after_workflow_action: function(frm) {
    frm.reload_doc();
  },
};
