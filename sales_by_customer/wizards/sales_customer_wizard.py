from odoo import fields,api,models,_
from odoo.tools.safe_eval import safe_eval
from datetime import datetime
import time
from odoo.tools.float_utils import float_round, float_compare, float_is_zero
import logging
import time
import xlsxwriter
import base64
import io


_logger = logging.getLogger(__name__)


class SalesCustomerWizard(models.TransientModel):
    _name = 'sales.customer.wizard'

    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    name = fields.Char('Nombre archivo', size=32)
    archivo = fields.Binary('Archivo', filters='.xls')

    def button_export_html(self):
        self.ensure_one()
        action = self.env.ref("sales_by_customer.action_report_sales_report_report_html")
        vals = action.read()[0]
        context = vals.get("context", {})
        if context:
            context = safe_eval(context)
        model = self.env["report.sales.customer.report"]
        report = model.create(self._prepare_customer_sale_report())
        context["active_id"] = report.id
        context["active_ids"] = report.ids
        vals["context"] = context
        print("!11111",vals)
        return vals

    def _prepare_customer_sale_report(self):
        self.ensure_one()
        return {
            "start_date": self.start_date,
            "end_date": self.end_date,
        }

    def print_report_excel(self):
        for w in self:
            dict = {}
            dict['fecha_hasta'] = w['start_date']
            dict['fecha_desde'] = w['end_date']

            f = io.BytesIO()
            libro = xlsxwriter.Workbook(f)
            hoja = libro.add_worksheet('Reporte')

            format1 = libro.add_format(
                {'font_size': 11, 'align': 'left', 'bold': True})
            format2 = libro.add_format({'font_size': 10, 'align': 'center','bold': True, 'bg_color': '#D3D3D3', 'num_format': '#,##0.00'})
            format3 = libro.add_format({'font_size': 10, 'align': 'right', 'num_format': '#,##0.00'})
            format4 = libro.add_format({'font_size': 10, 'align': 'right','bold': True, 'bg_color': '#ededed', 'num_format': '#,##0.00'})
            format5 = libro.add_format({'font_size': 10, 'align': 'left'})

            y = 3
            hoja.set_column(y, 0, 40)
            hoja.set_column(y, 1, 10)
            hoja.set_column(y, 2, 10)
            hoja.set_column(y, 3, 10)
            hoja.set_column(y, 4, 10)
            hoja.set_column(y, 5, 10)

            hoja.set_row(3, 30)

            hoja.write('A1', 'REPORTE DE VENTAS POR CLIENTE', format1)
            hoja.write('A2', 'REGISTROS DEL   ' + str(
                datetime.strftime(w['start_date'], '%d-%m-%Y')) + '    AL    ' + str(
                datetime.strftime(w['end_date'], '%d-%m-%Y')), format1)

            hoja.write(y, 0, 'NOMBRE DEL CLIENTE',format2)
            hoja.write(y, 1, 'TOTAL CON IVA',format2)
            hoja.write(y, 2, 'TOTAL SIN IVA',format2)
            hoja.write(y, 3, 'COSTO',format2)
            hoja.write(y, 4, 'CONTRIBUCIÓN',format2)
            hoja.write(y, 5, '%',format2)

            y += 1

            partner_ids = self.env['res.partner'].search([])
            print("11111",partner_ids)
            linear = []
            for partner in partner_ids:
                if partner.sale_order_count != 0:
                    domain = [('partner_id','=',partner.id),('create_date', '>=', w['start_date']), ('create_date', '<=', w['end_date'])]
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
#                            cost += line.product_id.standard_price * line.product_uom_qty
                            product_qty = line.product_uom._compute_quantity(line.product_uom_qty,
                                                                                line.product_id.uom_id,
                                                                                rounding_method='HALF-UP')
                            cost += line.product_id.standard_price * product_qty

                    if total_with_tax and total_without_tax:
                        contribution = total_without_tax - cost
                        percentage = round((contribution * 100) / total_without_tax)
                    if total_without_tax and total_with_tax:
                        linear.append({
                            'partner': str(partner.parent_id.name or '') + str(' ') + str(partner.name),
                            'total_with_tax': total_with_tax,
                            'total_without_tax': total_without_tax,
                            'cost':cost,
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
                hoja.write(y, 0, line['partner'],format5)
                hoja.write(y, 1, line['total_with_tax'], format3)
                hoja.write(y, 2, line['total_without_tax'],format3)
                hoja.write(y, 3, line['cost'],format3)
                hoja.write(y, 4, line['contribution'],format3)
                hoja.write(y, 5, line['percentage'],format3)
                y+=1

            hoja.write(y, 0, 'TOTAL',format2)
            hoja.write(y, 1, grandtotal_without_tax,format4)
            hoja.write(y, 2, grandtotal_with_tax,format4)
            hoja.write(y, 3, '---',format4)
            hoja.write(y, 4, grandtotal_with_contribution,format4)
            hoja.write(y, 5, '---', format4)

            libro.close()
            datos = base64.b64encode(f.getvalue())
            self.write({'archivo':datos, 'name':'sales_customer.xlsx'})

        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sales.customer.wizard',
            'res_id': self.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }