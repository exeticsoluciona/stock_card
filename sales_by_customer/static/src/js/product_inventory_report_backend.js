odoo.define('sales_by_customer.product_inventory_report_backend',  function (require) {
"use strict";
    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var ReportWidget = require("web.Widget");
    var iv_report_backend = AbstractAction.extend({
        hasControlPanel: true,
        init: function(parent, action) {
            this._super.apply(this, arguments);
            this.actionManager = parent;
            this.given_context = {};
            this.odoo_context = action.context;
            this.controller_url = action.context.url;
            if (action.context.context) {
                this.given_context = action.context.context;
            }
            this.given_context.active_id =
                action.context.active_id || action.params.active_id;
            this.given_context.model = action.context.active_model || false;
            this.given_context.ttype = action.context.ttype || false;
        },
        willStart: function() {
            return Promise.all([this._super.apply(this, arguments), this.get_html()]);
        },
        set_html: function() {
            var self = this;
            var def = Promise.resolve();
            if (!this.report_widget) {
                this.report_widget = new ReportWidget(this, this.given_context);
                def = this.report_widget.appendTo(this.$(".o_content"));
            }
            def.then(function() {
                self.report_widget.$el.html(self.html);
            });
        },
        start: function () {
                // Actions to do
            this.set_html();
            return this._super();
        },
        get_html: function() {
            var self = this;
            var defs = [];
            return this._rpc({
                model: this.given_context.model,
                method: "get_html",
                args: [self.given_context],
                context: self.odoo_context,
            }).then(function(result) {
                self.html = result.html;
                defs.push(self.update_cp());
                return $.when.apply($, defs);
            });
        },
        update_cp: function() {
            if (this.$buttons) {
                var status = {
                    breadcrumbs: this.actionManager.get_breadcrumbs(),
                    cp_content: {$buttons: this.$buttons},
                };
                return this.update_control_panel(status);
            }
        },
  // Functions according to the working of the widget.
});
  // Following code will attach the above widget to the defined client action
core.action_registry.add("product_inventory_report_backend", iv_report_backend);
return report_backend;
});