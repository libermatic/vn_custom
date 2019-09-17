import * as custom_scripts from './custom_scripts';
import * as scripts from './scripts';

// frappe.ui.form.on('Item Price', custom_scripts.item_price);
frappe.ui.form.on(
  'Sales Invoice Item',
  custom_scripts.sales_invoice.sales_invoice_item
);

frappe.provide('vn_custom');

vn_custom = { scripts };
