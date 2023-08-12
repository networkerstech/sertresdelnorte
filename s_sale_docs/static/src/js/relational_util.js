/** @odoo-module **/
import { X2ManyFieldDialog } from "@web/views/fields/relational_utils";
import { patch } from "@web/core/utils/patch";

patch(X2ManyFieldDialog.prototype, "sale_order_attachment_prevent_create_and_new_button", {
    setup() {
        this._super(...arguments);
        if (this.record.resModel == 'sale.order.attachment') {
            this.canCreate = false;
        }
    }
});