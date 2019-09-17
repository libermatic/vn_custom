import pick from 'lodash/pick';
import mapKeys from 'lodash/mapKeys';
import camelCase from 'lodash/camelCase';

import BranchDetails from '../components/BranchDetails.vue';

const DETAILS_FIELDS = [
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

const d = {
  STATE: 'MANIPUR',
  IMPS: true,
  RTGS: true,
  BRANCH: 'IMPHAL',
  NEFT: true,
  CITY: 'IMPHAL',
  DISTRICT: 'IMPHAL',
  CONTACT: '8003453333',
  MICR: '795240002',
  CENTRE: 'IMPHAL',
  ADDRESS:
    'IMPHAL HDFC BANK LTD TAMPHA EBEMA BUILDING, GANDHI AVENUE PIN 795001',
  BANK: 'HDFC Bank',
  BANKCODE: 'HDFC',
  IFSC: 'HDFC0001999',
};

async function set_details(frm) {
  function reset_values() {
    DETAILS_FIELDS.forEach(field => {
      frm.vue_details[field] = null;
    });
    frm.set_value({ bank: null, branch: null });
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
  return frm.set_value({
    bank: data_transformed.bank,
    branch: data_transformed.branch,
  });
}

function render_details(frm) {
  const { $wrapper } = frm.get_field('details_html');
  $wrapper.empty();
  return new Vue({
    data: Object.assign(
      { isLoading: false },
      ...DETAILS_FIELDS.map(field => ({ [field]: null }))
    ),
    el: $wrapper.html('<div />').children()[0],
    render: function(h) {
      return h(BranchDetails, {
        props: pick(this, ['isLoading', ...DETAILS_FIELDS]),
      });
    },
  });
}

export default {
  onload: function(frm) {
    frm.vue_details = render_details(frm);
  },
  refresh: set_details,
  ifsc: set_details,
};
