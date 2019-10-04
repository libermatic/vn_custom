import { bank_account_filters } from '../scripts/wire_transfer';

export default function wire_transfer_summary() {
  return {
    filters: [
      {
        fieldtype: 'Date Range',
        fieldname: 'date_range',
        label: 'Date Range',
        reqd: 1,
        default: [frappe.datetime.get_today(), frappe.datetime.get_today()],
      },
      {
        fieldtype: 'Select',
        fieldname: 'date_type',
        label: 'Date Type',
        reqd: 1,
        options: [
          'Created',
          'Modified',
          'Accepted',
          'Transfered',
          'Returned',
          'Failed',
        ],
        default: 'Created',
      },
      {
        fieldtype: 'Link',
        fieldname: 'bank_account',
        label: 'Bank Account',
        options: 'Account',
        get_query: () => ({ filters: bank_account_filters }),
      },
      {
        fieldtype: 'Select',
        fieldname: 'bank_mode',
        label: 'Bank Mode',
        options: ['', 'Third Party', 'NEFT', 'IMPS'],
      },
    ],
  };
}
