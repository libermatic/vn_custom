<template>
  <loading-indicator v-if="isLoading" />
  <div v-else-if="!bank" class="no-data">
    No data
  </div>
  <div v-else class="root">
    <dl class="width-full">
      <dt>Bank</dt>
      <dd>{{ bank }}</dd>
    </dl>
    <dl>
      <dt>Branch</dt>
      <dd>{{ branch }}</dd>
    </dl>
    <dl v-if="isExtended">
      <dt>IFSC</dt>
      <dd>{{ ifsc }}</dd>
    </dl>
    <dl v-if="micr">
      <dt>MICR</dt>
      <dd>{{ micr }}</dd>
    </dl>
    <dl class="width-full">
      <dt>Address</dt>
      <dd>{{ address || '-' }}</dd>
    </dl>
    <dl>
      <dt>City</dt>
      <dd>{{ city || '-' }}</dd>
    </dl>
    <dl>
      <dt>District</dt>
      <dd>{{ district || '-' }}</dd>
    </dl>
    <dl>
      <dt>State</dt>
      <dd>{{ state || '-' }}</dd>
    </dl>
    <dl>
      <dt>Contact</dt>
      <dd>{{ contact || '-' }}</dd>
    </dl>
    <dl class="width-full">
      <dt>Services</dt>
      <dd>
        <span :class="{ badge: true, enabled: imps }">IMPS</span>
        <span :class="{ badge: true, enabled: rtgs }">RTGS</span>
        <span :class="{ badge: true, enabled: neft }">NEFT</span>
      </dd>
    </dl>
  </div>
</template>

<script>
import LoadingIndicator from './LoadingIndicator.vue';
export default {
  components: { LoadingIndicator },
  props: {
    isLoading: { type: Boolean, default: false },
    isExtended: { type: Boolean, default: false },
    ifsc: { type: String, default: null },
    bank: { type: String, default: null },
    branch: { type: String, default: null },
    micr: { type: String, default: null },
    address: { type: String, default: null },
    contact: { type: String, default: null },
    city: { type: String, default: null },
    district: { type: String, default: null },
    state: { type: String, default: null },
    imps: { type: Boolean, default: null },
    rtgs: { type: Boolean, default: null },
    neft: { type: Boolean, default: null },
  },
};
</script>

<style lang="scss" scoped>
.no-data {
  text-align: center;
  color: #8d99a6;
  margin-top: 2em;
}
.root {
  display: flex;
  flex-flow: row wrap;
  > dl {
    font-size: 12px;
    margin: 0 1em 0.5em;
  }
  dt {
    font-weight: normal;
    color: #8d99a6;
  }
}
.width-full {
  width: 100%;
}
.enabled {
  background-color: #98d85b;
}
</style>
