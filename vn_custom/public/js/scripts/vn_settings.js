export default {
  refresh: function(frm) {
    frm.add_custom_button('Setup', async function() {
      try {
        await frappe.call({
          method: 'vn_custom.install.setup_defaults',
          freeze: true,
        });
      } finally {
        frm.reload_doc();
      }
    });
  },
};
