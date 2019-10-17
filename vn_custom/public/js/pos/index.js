import flowRight from 'lodash/flowRight';

import withQtyInList from './withQtyInList.js';

export const extend_items = flowRight([withQtyInList]);
