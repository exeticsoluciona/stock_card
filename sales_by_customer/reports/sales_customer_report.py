from odoo import fields,api,models
class CustomerLinear(models.TransientModel):
    _name = 'customer.linear'

    partner = fields.Char(string="Partner")
    total_without_tax = fields.Char(string="Total Without Tax")
    total_with_tax = fields.Char(string="Total With Tax")
    cost = fields.Char(string="cost")
    contribution = fields.Char(string="contribution")
    percentage = fields.Char(string="percentage")


class ReportSalesReport(models.TransientModel):
    _name = 'report.sales.customer.report'

    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    grandtotal_without_tax = fields.Float(string='GrandTotal Without Tax')
    grandtotal_with_tax = fields.Float(string='GrandTotal With Tax')
    grandtotal_with_contribution = fields.Float(string='Contribution')
    liners_ids = fields.Many2many(comodel_name="customer.linear",string="Liners")

    def _get_html(self):
        result = {}
        rcontext = {}
        report = self.browse(self._context.get("active_id"))
        partner_ids = self.env['res.partner'].search([])
        linear = []
        for partner in partner_ids:
            if partner.sale_order_count != 0:
                domain = [('partner_id', '=', partner.id), ('create_date', '>=', report.start_date),
                          ('create_date', '<=', report.end_date)]
                order_ids = self.env['sale.order'].search(domain)
                total_without_tax = 0.0
                total_with_tax = 0.0
                cost = 0.0
                contribution = 0.0
                percentage = 0.0
                for order in order_ids:
                    for line in order.order_line:
                        total_without_tax += line.price_subtotal
                        total_with_tax += line.price_unit * line.product_uom_qty
#                        cost += line.product_id.standard_price * line.product_uom_qty
                        product_qty = line.product_uom._compute_quantity(line.product_uom_qty,
                                                                         line.product_id.uom_id,
                                                                         rounding_method='HALF-UP')
                        cost += line.product_id.standard_price * product_qty

                if total_with_tax and total_without_tax:
                    contribution = total_without_tax -  cost
#                    percentage = round((total_without_tax - (cost or 0)) * 100 / (cost or 1))
                    percentage = round((contribution * 100) / total_without_tax)
                if total_without_tax and total_with_tax:
                    report.liners_ids = [(0,0,{
                        'partner': str(partner.parent_id.name or '') + str(' ') + str(partner.name),
                        'total_without_tax': "{:,.2f}".format(total_without_tax),
                        'total_with_tax': "{:,.2f}".format(total_with_tax),
                        'cost': "{:,.2f}".format(cost),
                        'contribution': "{:,.2f}".format(contribution),
                        'percentage': "{:.2f}".format(percentage),
                    })]
                    linear.append({
                        'partner': str(partner.parent_id.name or '') + str(' ') + str(partner.name),
                        'total_without_tax': total_without_tax,
                        'total_with_tax': total_with_tax,
                        'cost': cost,
                        'contribution': contribution,
                        'percentage': percentage,
                    })
        grandtotal_without_tax = 0.0
        grandtotal_with_tax = 0.0
        grandtotal_with_contribution = 0.0
        for line in linear:
            grandtotal_without_tax += line['total_without_tax']
            grandtotal_with_tax += line['total_with_tax']
            grandtotal_with_contribution += line['contribution']

        report.grandtotal_without_tax = "{:.2f}".format(grandtotal_without_tax)
        report.grandtotal_with_tax = "{:.2f}".format(grandtotal_with_tax)
        report.grandtotal_with_contribution = "{:.2f}".format(grandtotal_with_contribution)

        # result.update({
        #     "linear" : linear,
        #     "grandtotal_without_tax" : grandtotal_without_tax,
        #     "grandtotal_with_tax" : grandtotal_with_tax,
        #     "grandtotal_with_contribution" : grandtotal_with_contribution,
        # })
        if report:
            rcontext["o"] = report
            result["html"] = self.env.ref(
                "sales_by_customer.report_sales_customer_report_html"
            ).render(rcontext)
        return result

    @api.model
    def get_html(self, given_context=None):
        return self.with_context(given_context)._get_html()