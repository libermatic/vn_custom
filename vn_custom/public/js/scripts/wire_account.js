import pick from 'lodash/pick';
import mapKeys from 'lodash/mapKeys';
import camelCase from 'lodash/camelCase';
import { createApp } from 'vue';

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

export async function get_ifsc_details(ifsc) {
  if (!ifsc) {
    return;
  }
  const response = await fetch(`https://ifsc.razorpay.com/${ifsc}`);
  if (response.status !== 200) {
    return;
  }
  const data = await response.json();
  if (!data) {
    return;
  }
  return mapKeys(data, (v, k) => camelCase(k));
}

async function set_and_render_ifsc(frm, isExtended = false) {
  const { $wrapper } = frm.get_field('details_html');
  $wrapper.empty();

  const { ifsc } = frm.doc;

  const data = await get_ifsc_details(ifsc);
  if (!data) {
    return;
  }

  if (frm.doc.docstatus === 0) {
    ['bank', 'branch'].forEach((field) => {
      if (data[field]) {
        frm.set_value(field, data[field]);
      }
    });
  }

  render_ifsc(data, $wrapper.html('<div />').children()[0], isExtended);
}

export function render_ifsc(data, node, isExtended = false) {
  const props = Object.assign(
    {
      isLoading: false,
      isExtended,
    },
    ...DETAILS_FIELDS.map((field) => ({ [field]: data[field] }))
  );

  createApp(BranchDetails, props).mount(node);
}

export default {
  refresh: set_and_render_ifsc,
  ifsc: set_and_render_ifsc,
};
