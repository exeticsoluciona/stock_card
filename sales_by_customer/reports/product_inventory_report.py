from odoo import fields,api,models

class InventoryLiners(models.TransientModel):
    _name = 'inventory.liners'

    default_code = fields.Char(string="Default Code")
    categ_id = fields.Char(string="categ_id")
    product_id = fields.Char(string="NAME OF PRODUCT")
    lot_id = fields.Char(string="NAME OF PRODUCT")
    lst_price = fields.Char(string="List Price")
    standard_price = fields.Char(string="Standard Price")
    quantity = fields.Char(string="quantity")
    forecast = fields.Char(string="forecast")
    uom_id = fields.Char(string="uom")

class ProductTotalQty(models.TransientModel):
    _name = 'product.total.qty'

    categ_name = fields.Char(string="Categ")
    total_value = fields.Char(string="QTY ON HAND")


class ReportProductInventory(models.TransientModel):
    _name = 'report.product.inventory.report'

    location_id = fields.Many2one('stock.location', string="Location")
    categ_ids = fields.Many2many('product.category', string="Category")
    inventory_liners_ids = fields.Many2many(comodel_name='inventory.liners',string="Inventor Liners")
    product_total_qty_ids = fields.Many2many(comodel_name='product.total.qty',string="Product Total Qty")

    def _get_html(self):
        result = {}
        rcontext = {}
        report = self.browse(self._context.get("active_id"))

        categ_name = ''
        list_cated_ids = []
        for categ in report.categ_ids:
            categ_name += ',' + ' ' + categ.name
            list_cated_ids.append(categ.id)

        quant_ids = self.env['stock.quant'].search([('location_id', '=', report.location_id.id)],order='product_id asc')

        categ_dic = {}
        total_categ_on_hand = {}
        if quant_ids:
            for quant in quant_ids:
                if quant.product_id.active and quant.product_id.categ_id.id in list_cated_ids:
                    if quant.product_id.categ_id.name in categ_dic:
                        # append the new number to the existing array at this slot
                        categ_dic[quant.product_id.categ_id.name].append({
                            'default_code': quant.product_id.default_code,
                            'categ_id': quant.product_id.categ_id.name,
                            'product_id': quant.product_tmpl_id.name,
                            'lst_price': "{:.2f}".format(quant.product_id.lst_price),
                            'lot_id': quant.lot_id.name or '',
                            'standard_price': "{:.2f}".format(quant.product_id.standard_price),
                            'quantity': "{:.2f}".format(quant.quantity),
                            'forecast': "{:.2f}".format(quant.product_tmpl_id.virtual_available,),
                            'uom_id': quant.product_id.uom_id.name,
                        })
                    else:
                        # create a new array in this slot
                        categ_dic[quant.product_id.categ_id.name] = [{
                            'default_code': quant.product_id.default_code,
                            'categ_id': quant.product_id.categ_id.name,
                            'product_id': quant.product_tmpl_id.name,
                            'lst_price': "{:.2f}".format(quant.product_id.lst_price),
                            'lot_id': quant.lot_id.name or '',
                            'standard_price': "{:.2f}".format(quant.product_id.standard_price),
                            'quantity': "{:.2f}".format(quant.quantity),
                            'forecast': "{:.2f}".format(quant.product_tmpl_id.virtual_available,),
                            'uom_id': quant.product_id.uom_id.name,
                        }]
        total_qty_on_hand = {}
        for categ in categ_dic.values():
            total_on_hand = 0
            for line in categ:
                total_on_hand += float(line.get('quantity'))
                total_qty_on_hand.update({
                    line.get('categ_id') : total_on_hand,
                })
                report.inventory_liners_ids = [(0, 0, line)]

        if total_qty_on_hand:
            for qty in total_qty_on_hand:
                report.product_total_qty_ids = [(0,0,{'categ_name':qty,'total_value':"{:.2f}".format(total_qty_on_hand[qty])})]

        if report:
            rcontext["o"] = report
            result["html"] = self.env.ref(
                "sales_by_customer.report_product_inventory_report_html"
            ).render(rcontext)
        return result

    @api.model
    def get_html(self, given_context=None):
        return self.with_context(given_context)._get_html()