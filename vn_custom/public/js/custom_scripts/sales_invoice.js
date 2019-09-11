const sales_invoice_item = {
  item_code: async function(frm, cdt, cdn) {
    const { item_code } = frappe.get_doc(cdt, cdn) || {};
    if (item_code) {
      const { message: { vn_mrp, vn_valuation } = {} } = await frappe.call({
        method: 'vn_custom.api.item.get_other_prices',
        args: { item_code },
      });
      frappe.model.set_value(cdt, cdn, { vn_mrp, vn_valuation });
    } else {
      frappe.model.set_value(cdt, cdn, { vn_mrp: null, vn_valuation: null });
    }
  },
};

export default {
  sales_invoice_item,
};
