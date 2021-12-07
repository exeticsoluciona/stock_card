from odoo import fields,api,models,_
from odoo.tools.safe_eval import safe_eval
import logging
import time
import xlsxwriter
import base64
import io
from datetime import datetime

_logger = logging.getLogger(__name__)


class ProductInventoryWizard(models.TransientModel):
    _name = 'product.inventory.wizard'

    location_id = fields.Many2one('stock.location',string="Location")
    categ_ids = fields.Many2many('product.category',string="Category")
    name = fields.Char('Nombre archivo', size=32)
    archivo = fields.Binary('Archivo', filters='.xls')

    def button_export_html(self):
        self.ensure_one()
        action = self.env.ref("sales_by_customer.action_report_product_inventory_html")
        vals = action.read()[0]
        context = vals.get("context", {})
        if context:
            context = safe_eval(context)
        model = self.env["report.product.inventory.report"]
        report = model.create(self._prepare_customer_sale_report())
        context["active_id"] = report.id
        context["active_ids"] = report.ids
        vals["context"] = context
        print("!11111",vals)
        return vals

    def _prepare_customer_sale_report(self):
        self.ensure_one()
        return {
            "location_id": self.location_id.id,
            "categ_ids": self.categ_ids,
        }

    def print_report_excel(self):
        for w in self:
            dict = {}
            dict['location_id'] = w['location_id']
            dict['categ_ids'] = w['categ_ids']

            categ_name = ''
            list_cated_ids = []
            for categ in w['categ_ids']:
                categ_name += ',' + ' ' + categ.name
                list_cated_ids.append(categ.id)

            f = io.BytesIO()
            libro = xlsxwriter.Workbook(f)
            hoja = libro.add_worksheet('Reporte')
            y = 0
            format4 = libro.add_format({'font_size': 12, 'align': 'center', 'bold': True})
            format5 = libro.add_format({'font_size': 10, 'align': 'center'})
            format6 = libro.add_format({'font_size': 10, 'align': 'right', 'num_format': '#,##0.00'})
            format7 = libro.add_format({'font_size': 10, 'align': 'right', 'num_format': 'dd/mm/yy'})

            hoja.merge_range('A' + str(y + 1) + ':' + 'L' + str(y + 1), 'REPORTE DE INVENTARIO',format4)
#            y+=1
#            hoja.merge_range('A' + str(y + 1) + ':' + 'B' + str(y + 1), 'FECHA INICIAL',format5)
#            hoja.merge_range('C' + str(y + 1) + ':' + 'D' + str(y + 1), '',format5)
#            hoja.merge_range('E' + str(y + 1) + ':' + 'F' + str(y + 1), 'FECHA FINAL',format5)
#            hoja.merge_range('G' + str(y + 1) + ':' + 'H' + str(y + 1), '',format5)
            y+=1
            hoja.merge_range('A' + str(y + 1) + ':' + 'B' + str(y + 1), 'EMITIDO POR', format5)
            hoja.merge_range('C' + str(y + 1) + ':' + 'D' + str(y + 1), self.env.user.name, format5)
            hoja.merge_range('E' + str(y + 1) + ':' + 'F' + str(y + 1), 'FECHA DE EMISIÓN', format5)
            hoja.merge_range('G' + str(y + 1) + ':' + 'H' + str(y + 1), datetime.today().date(), format7)
            y+=1
            hoja.merge_range('A' + str(y + 1) + ':' + 'B' + str(y + 1), 'UBICACION', format5)
            hoja.merge_range('C' + str(y + 1) + ':' + 'D' + str(y + 1), w['location_id'].name, format5)
            hoja.merge_range('E' + str(y + 1) + ':' + 'F' + str(y + 1), 'CATEGORÍAS', format5)
            hoja.merge_range('G' + str(y + 1) + ':' + 'H' + str(y + 1), categ_name, format5)
            y+=1

            format2 = libro.add_format({'font_size': 8, 'align': 'distributed', 'bold': True, 'bg_color': '#D3D3D3'})
            format1 = libro.add_format({'font_size': 12, 'align': 'center', 'bold': True, 'bg_color': '#D3D3D3'})

            hoja.set_column(0, 0, 10)
            hoja.set_column(1, 1, 25)
            hoja.set_column(2, 2, 40)
            hoja.set_column(3, 3, 20)
            hoja.set_column(4, 9, 10)
            hoja.set_column(10, 10, 13)
            hoja.set_column(11, 11, 10)
            hoja.set_row(3, 30)

            hoja.write(y, 0, 'CODIGO',format2)
            hoja.write(y, 1, 'CATEGORIA',format2)
            hoja.write(y, 2, 'NOMBRE DEL PRODUCTO',format2)
            hoja.write(y, 3, 'NUMERO DE LOTE', format2)
            hoja.write(y, 4, 'PRECIO DE VENTA', format2)
            hoja.write(y, 5, 'COSTO UNITARIO', format2)
            hoja.write(y, 6, 'EXISTENCIA ACTUAL', format2)
            hoja.write(y, 7, 'EXISTENCIA PREVISTA', format2)
            hoja.write(y, 8, 'UNIDAD DE MEDIDA', format2)
            hoja.write(y, 9, 'UDM SECUNDARIA', format2)
            hoja.write(y, 10, 'EXISTENCIA ACTUAL EN UDM SECUNDARIA', format2)
            hoja.write(y, 11, 'COSTO TOTAL', format2)

            y += 1
            quant_ids = self.env['stock.quant'].search([('location_id','=',w['location_id'].id)],order='product_id asc')




            categ_dic = {}
            if quant_ids:
                for quant in quant_ids:
                    second_uom = quant.product_id.sh_secondary_uom or quant.product_id.uom_id
                    if quant.product_id.active and quant.product_id.categ_id.id in list_cated_ids :
                        if quant.product_id.categ_id.name in categ_dic:
                            # append the new number to the existing array at this slot
                            categ_dic[quant.product_id.categ_id.name].append({
                                'default_code': quant.product_id.default_code,
                                'categ_id': quant.product_id.categ_id.name,
                                'product_id': quant.product_id.name,
                                'lst_price': "{:.2f}".format(quant.product_id.lst_price),
                                'lot_id': quant.lot_id.name or '',
                                'standard_price': "{:.2f}".format(quant.product_id.standard_price),
                                'quantity': "{:.2f}".format(quant.quantity),
                                'forecast': "{:.2f}".format(quant.product_tmpl_id.virtual_available,),
                                'uom_id': quant.product_id.uom_id.name,
                                'second_uom_id': quant.product_id.sh_secondary_uom.name or '---',
                                'current_udm': "{:.2f}".format(quant.product_uom_id._compute_quantity(quant.quantity, second_uom)),
                                'costo_total': "{:.2f}".format(quant.product_id.standard_price * quant.quantity),
                            })


                        else:
                            # create a new array in this slot
                            categ_dic[quant.product_id.categ_id.name] = [{
                                'default_code': quant.product_id.default_code,
                                'categ_id': quant.product_id.categ_id.name,
                                'product_id': quant.product_id.name,
                                'lot_id': quant.lot_id.name or '',
                                'lst_price': "{:.2f}".format(quant.product_id.lst_price),
                                'standard_price': "{:.2f}".format(quant.product_id.standard_price),
                                'quantity': "{:.2f}".format(quant.quantity),
                                'forecast': "{:.2f}".format(quant.product_tmpl_id.virtual_available),
                                'uom_id': quant.product_id.uom_id.name,
                                'second_uom_id': quant.product_id.sh_secondary_uom.name or quant.product_id.uom_id.name or '---',
                                'current_udm': "{:.2f}".format(quant.product_uom_id._compute_quantity(quant.quantity, second_uom)),
                                'costo_total': "{:.2f}".format(quant.product_id.standard_price * quant.quantity),
                            }]
            total_qty_on_hand = {}
            total_costo = 0.0
            for categ in categ_dic.values():
                total_on_hand = 0.0
                for line in categ:
                    print("111111",line)
                    total_on_hand += float(line.get('quantity'))
                    total_costo += float(line.get('costo_total'))
                    total_qty_on_hand.update({
                        line.get('categ_id'): total_on_hand,
                    })
                    hoja.write(y, 0, line.get('default_code'))
                    hoja.write(y, 1, line.get('categ_id'))
                    hoja.write(y, 2, line.get('product_id'))
                    hoja.write(y, 3, line.get('lot_id'))
                    hoja.write(y, 4, line.get('lst_price'),format6)
                    hoja.write(y, 5, line.get('standard_price'),format6)
                    hoja.write(y, 6, line.get('quantity'),format6)
                    hoja.write(y, 7, line.get('forecast'),format6)
                    hoja.write(y, 8, line.get('uom_id'))
                    hoja.write(y, 9, line.get('second_uom_id'))
                    hoja.write(y, 10, line.get('current_udm'),format6)
                    hoja.write(y, 11, line.get('costo_total'),format6)
                    y += 1
            hoja.write(y, 10, 'COSTO TOTAL')
            hoja.write(y, 11, total_costo)
#            y += 3
#            hoja.merge_range('C'+str(y+1) + ':' + 'D'+ str(y+1), 'SUMMARY BY PRODUCT CATEGORY',format1)
#            y += 1
#            hoja.write(y, 2, 'Categoría de productos',format1)
#            hoja.write(y, 3, 'Total de existencias',format1)
#            y+=1
#            if total_qty_on_hand:
#                for qty in total_qty_on_hand:
#                    hoja.write(y, 2, qty, format1)
#                    hoja.write(y, 3, "{:.2f}".format(total_qty_on_hand[qty]), format1)
#                    y+=1

            libro.close()
            datos = base64.b64encode(f.getvalue())
            self.write({'archivo': datos, 'name': 'product_inventory.xlsx'})

        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'product.inventory.wizard',
            'res_id': self.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }