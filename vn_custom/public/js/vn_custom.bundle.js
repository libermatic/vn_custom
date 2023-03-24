import * as cscripts from './custom_scripts';
import * as scripts from './scripts';
import * as reports from './reports';
import { __version__ } from './version';

frappe.provide('vn_custom');

vn_custom = { __version__, scripts, reports };

function get_doctype(import_name) {
  return import_name
    .split('_')
    .map((w) => w[0].toUpperCase() + w.slice(1))
    .join(' ');
}

Object.keys(cscripts).forEach((import_name) => {
  const get_handler = cscripts[import_name];
  frappe.ui.form.on(get_doctype(import_name), get_handler);
});
