<template>
  <loading-indicator v-if="isLoading" />
  <div v-else-if="!bank" class="no-data">
    No data
  </div>
  <div v-else class="root">
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
    <dl v-if="micr" class="width-full">
      <dt>MICR</dt>
      <dd>{{ micr }}</dd>
    </dl>
    <dl>
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
    margin: 0 1em 1em;
  }
  dt {
    font-size: 12px;
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
