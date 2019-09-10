async function toggle_rate(frm) {
  const [
    selling_price_list,
    { message: { vn_has_margin_price: has_margin_price = 0 } = {} },
  ] = await Promise.all([
    frappe.db.get_single_value('Selling Settings', 'selling_price_list'),
    frappe.db.get_value('Item', frm.doc.item_code, 'vn_has_margin_price'),
  ]);
  frm.toggle_enable(
    'price_list_rate',
    !(frm.doc.price_list === selling_price_list && has_margin_price)
  );
}

export default {
  refresh: function(frm) {
    if (!frm.doc.__islocal) {
      toggle_rate(frm);
    }
  },
};
