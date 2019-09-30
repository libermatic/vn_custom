import pick from 'lodash/pick';
import mapKeys from 'lodash/mapKeys';
import camelCase from 'lodash/camelCase';

import BranchDetails from '../components/BranchDetails.vue';

const DETAILS_FIELDS = [
  'ifsc',
  'bank',
  'branch',
  'micr',
  'address',
  'contact',
  'city',
  'district',
  'state',
  'imps',
  'rtgs',
  'neft',
];

export async function set_details(frm) {
  function reset_values() {
    DETAILS_FIELDS.forEach(field => {
      frm.vue_details[field] = null;
    });
  }

  const { ifsc } = frm.doc;
  if (!ifsc) {
    reset_values();
    return;
  }
  frm.vue_details.isLoading = true;
  const response = await fetch(`https://ifsc.razorpay.com/${ifsc}`);
  frm.vue_details.isLoading = false;
  if (response.status !== 200) {
    reset_values();
    return;
  }
  const data = await response.json();
  if (!data) {
    reset_values();
    return;
  }
  const data_transformed = mapKeys(data, (v, k) => camelCase(k));
  DETAILS_FIELDS.forEach(field => {
    frm.vue_details[field] = data_transformed[field];
  });
  return data_transformed;
}

async function set_details_and_values(frm) {
  const data = await set_details(frm);
  if (frm.doc.docstatus === 0) {
    ['bank', 'branch'].forEach(field => {
      if (data && data[field]) {
        frm.set_value(field, data[field]);
      }
    });
  }
}

export function render_details(frm, el, isExtended = false) {
  return new Vue({
    data: Object.assign(
      { isLoading: false, isExtended },
      ...DETAILS_FIELDS.map(field => ({ [field]: null }))
    ),
    el,
    render: function(h) {
      return h(BranchDetails, {
        props: pick(this, ['isLoading', 'isExtended', ...DETAILS_FIELDS]),
      });
    },
  });
}

export default {
  onload: function(frm) {
    const { $wrapper } = frm.get_field('details_html');
    $wrapper.empty();
    frm.vue_details = render_details(
      frm,
      $wrapper.html('<div />').children()[0]
    );
  },
  refresh: set_details_and_values,
  ifsc: set_details_and_values,
};
