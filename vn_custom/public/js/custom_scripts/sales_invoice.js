export const sales_invoice_item = {
  item_code: async function (frm, cdt, cdn) {
    const { item_code } = frappe.get_doc(cdt, cdn);
    if (item_code) {
      const {
        message: { stock_uom, sales_uom },
      } = await frappe.db.get_value('Item', item_code, [
        'stock_uom',
        'sales_uom',
      ]);
      await frappe.model.set_value(cdt, cdn, { uom: stock_uom || sales_uom });
    }
  },

  uom: async function (frm, cdt, cdn) {
    const { item_code, uom } = frappe.get_doc(cdt, cdn) || {};
    if (item_code) {
      const { message: { vn_mrp = 0, vn_valuation = 0 } = {} } =
        await frappe.call({
          method: 'vn_custom.api.item.get_other_prices',
          args: { item_code, uom },
        });
      frappe.model.set_value(cdt, cdn, { vn_mrp, vn_valuation });
    } else {
      frappe.model.set_value(cdt, cdn, { vn_mrp: null, vn_valuation: null });
    }
  },
};

export const sales_invoice = {
  setup: function (frm) {
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
