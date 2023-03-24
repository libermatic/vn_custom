async function set_other_prices(frm, cdt, cdn) {
  const { item_code, uom } = frappe.get_doc(cdt, cdn) || {};
  if (item_code) {
    const {
      message: { vn_mrp = 0, vn_valuation = 0 } = {},
    } = await frappe.call({
      method: 'vn_custom.api.item.get_other_prices',
      args: { item_code, uom },
    });
    frappe.model.set_value(cdt, cdn, { vn_mrp, vn_valuation });
  } else {
    frappe.model.set_value(cdt, cdn, { vn_mrp: null, vn_valuation: null });
  }
  },
};

const sales_invoice = {
  setup: function (frm) {
    console.log('setup');
    frm.set_query('uom', 'items', function (doc, cdt, cdn) {
      const { item_code } = frappe.get_doc(cdt, cdn);
      if (item_code) {
        return {
          query: 'vn_custom.api.item.get_uom',
          filters: { item_code },
        };
}
    });
  },
};

export default {
  sales_invoice_item,
  sales_invoice,
};
