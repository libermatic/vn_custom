export default function cash_ledger() {
  return {
    onload: async function(rep) {
      const {
        message: { default_cash_account } = {},
      } = await frappe.db.get_value(
        'Company',
        frappe.defaults.get_user_default('company'),
        'default_cash_account'
      );
      rep.set_filter_value('cash_account', default_cash_account);
    },
    filters: [
      {
        fieldtype: 'Date Range',
        fieldname: 'date_range',
        label: 'Date Range',
        reqd: 1,
        default: [frappe.datetime.get_today(), frappe.datetime.get_today()],
      },
      {
        fieldtype: 'Link',
        fieldname: 'cash_account',
        label: 'Cash Account',
        options: 'Account',
        only_select: 1,
        get_query: () => ({ filters: { account_type: 'Cash', is_group: 0 } }),
        reqd: 1,
      },
      {
        fieldtype: 'Link',
        fieldname: 'cost_center',
        label: 'Cost Center',
        options: 'Cost Center',
        only_select: 1,
        get_query: () => ({ filters: { is_group: 0 } }),
      },
    ],
  };
}
