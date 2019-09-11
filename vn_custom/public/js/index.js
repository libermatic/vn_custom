import * as custom_scripts from './custom_scripts';

// frappe.ui.form.on('Item Price', custom_scripts.item_price);
frappe.ui.form.on(
  'Sales Invoice Item',
  custom_scripts.sales_invoice.sales_invoice_item
);
