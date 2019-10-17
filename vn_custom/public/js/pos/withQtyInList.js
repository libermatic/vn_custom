export default function withQtyInList(Items) {
  const isClass = Items instanceof Function || Items instanceof Class;
  if (!isClass) {
    return Items;
  }
  return class ItemsWithQtyInList extends Items {
    get_item_html(item) {
      const price_list_rate = format_currency(
        item.price_list_rate,
        this.currency
      );
      const { item_code, item_name, item_image, actual_qty, stock_uom } = item;
      const item_title = item_name || item_code;
      const qty_text = actual_qty ? `${actual_qty} ${stock_uom}` : '-';

      const template = `
        <div class="pos-item-wrapper image-view-item" data-item-code="${escape(
          item_code
        )}">
          <div class="image-view-header">
            <div>
              <a class="grey list-id" data-name="${item_code}" title="${item_title}">
                ${item_title}
              </a>
            </div>
          </div>
          <div class="image-view-body">
            <a  data-item-code="${item_code}"
              title="${item_title}"
            >
              <div class="image-field"
                style="${
                  !item_image ? 'background-color: #fafbfc;' : ''
                } border: 0px;"
              >
                ${
                  !item_image
                    ? `<span class="placeholder-text">
                    ${frappe.get_abbr(item_title)}
                  </span>`
                    : ''
                }
                ${
                  item_image
                    ? `<img src="${item_image}" alt="${item_title}">`
                    : ''
                }
              </div>

              <div class="price-info" style="${
                actual_qty
                  ? 'background-color: rgba(152, 216, 91, 0.6); color: rgba(54, 65, 76, 0.8);'
                  : ''
              }">
                <div>${qty_text}</div>
                <div>${price_list_rate}</div>
              </div>
            </a>
          </div>
        </div>
      `;

      return template;
    }
  };
}
