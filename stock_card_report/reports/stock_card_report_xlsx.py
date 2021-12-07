# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class ReportStockCardReportXlsx(models.AbstractModel):
    _name = "report.stock_card_report.report_stock_card_report_xlsx"
    _description = "Stock Card Report XLSX"
    _inherit = "report.report_xlsx.abstract"

    def generate_xlsx_report(self, workbook, data, objects):
        self._define_formats(workbook)
        for product in objects.product_ids:
            for ws_params in self._get_ws_params(workbook, data, product):
                ws_name = ws_params.get("ws_name")
                ws_name = self._check_ws_name(ws_name)
                ws = workbook.add_worksheet(ws_name)
                generate_ws_method = getattr(self, ws_params["generate_ws_method"])
                generate_ws_method(workbook, ws, ws_params, data, objects, product)

    def _get_ws_params(self, wb, data, product):
        print(">>>>>>>>>",self._render('final_average'))
        filter_template = {
            "1_date_from": {
                "header": {"value": "De la fecha"},
                "data": {
                    "value": self._render("date_from"),
                    "format": self.format_tcell_date_center,
                },
            },
            "2_date_to": {
                "header": {"value": "A la fecha"},
                "data": {
                    "value": self._render("date_to"),
                    "format": self.format_tcell_date_center,
                },
            },
            "3_location": {
                "header": {"value": "Ubicación"},
                "data": {
                    "value": self._render("location"),
                    "format": self.format_tcell_center,
                },
            },
            "4_udm_principal": {
                "header": {"value": "UDM Principal"},
                "data": {
                    "value": product.uom_id.name,
                    "format": self.format_tcell_center,
                },
            },
            "5_udm_secundaria": {
                "header": {"value": "UDM Secundaria"},
                "data": {
                    "value": product.sh_secondary_uom.name,
                    "format": self.format_tcell_center,
                },
            },
            "6_avg_cost": {
                "header": {"value": "Costo promedio / kardex"},
                "data": {
                    "value": self._render('final_average'),
                    "format": self.format_tcell_amount_right,
                },
            },
        }
        initial_template = {
            "1_ref": {
                "data": {"value": "Saldo Inicial", "format": self.format_tcell_center},
                "colspan": 5,
            },
            "2_balance": {
                "data": {
                    "value": self._render("balance"),
                    "format": self.format_tcell_amount_right,
                }
            },
        }
        stock_card_template = {
            "1_date": {
                "header": {"value": "Fecha"},
                "data": {
                    "value": self._render("date"),
                    "format": self.format_tcell_date_center,
                },
                "width": 15,
            },
            "2_reference": {
                "header": {"value": "Referencia"},
                "data": {
                    "value": self._render("reference"),
                    "format": self.format_tcell_left,
                },
                "width": 25,
            },
            "3_cost": {
                "header": {"value": "Precio de costo"},
                "data": {
                    "value": self._render("nearest_standard_price"),
                },
                "width": 15,
            },
            "4_input": {
                "header": {"value": "Entradas"},
                "data": {"value": self._render("input")},
                "width": 15,
            },
            "5_output": {
                "header": {"value": "Salidas"},
                "data": {"value": self._render("output")},
                "width": 15,
            },
            "6_balance": {
                "header": {"value": "Saldo"},
                "data": {"value": self._render("balance")},
                "width": 15,
            },
        }
        stock_card_total = {
            "1_blank": {
                "header": {"value": ""},
                "data": {
                    "value": '',
                },
                "width": 15,
            },
            "2_total_udm_principal": {
                "header": {"value": "TOTAL EN UDM Principal"},
                "data": {
                    "value": "TOTAL EN UDM Principal",
                    "format": self.format_tcell_amount_right_bold,
                },
                "width": 15,
            },
            "3_blank": {
                "header": {"value": ""},
                "data": {
                    "value": "",
                },
                "width": 15,
            },
            "4_total_udm_entradas": {
                "header": {"value": ""},
                "data": {
                    "value": self._render('total_entradas'),
                    "format": self.format_tcell_amount_right_bold,
                },
                "width": 15,
            },
            "5_total_udm_salidas": {
                "header": {"value": ""},
                "data": {
                    "value": self._render('total_salidas'),
                    "format": self.format_tcell_amount_right_bold,
                },
                "width": 15,
            },
            "6_total_udm_balance": {
                "header": {"value": ""},
                "data": {
                    "value": self._render('total_balance'),
                    "format": self.format_tcell_amount_right_bold,
                },
                "width": 15,
            },
        }
        stock_card_secundari = {
            "1_blank": {
                "header": {"value": ""},
                "data": {
                    "value": '',
                },
                "width": 15,
            },
            "2_total_udm_principal": {
                "header": {"value": "TOTAL EN UDM Secundaria"},
                "data": {
                    "value": "TOTAL EN UDM Secundaria",
                    "format": self.format_tcell_amount_right_bold,
                },
                "width": 15,
            },
            "3_blank": {
                "header": {"value": ""},
                "data": {
                    "value": "",
                },
                "width": 15,
            },
            "4_total_udm_entradas": {
                "header": {"value": ""},
                "data": {
                    "value": self._render('total_se_entradas'),
                    "format": self.format_tcell_amount_right_bold,
                },
                "width": 15,
            },
            "5_total_udm_salidas": {
                "header": {"value": ""},
                "data": {
                    "value": self._render('total_se_salidas'),
                    "format": self.format_tcell_amount_right_bold,
                },
                "width": 15,
            },
            "6_total_udm_balance": {
                "header": {"value": ""},
                "data": {
                    "value": self._render('total_se_balance'),
                    "format": self.format_tcell_amount_right_bold,
                },
                "width": 15,
            },
        }

        ws_params = {
            "ws_name": product.name,
            "generate_ws_method": "_stock_card_report",
            "title": "Reporte de Kardex - {}".format(product.name),
            "wanted_list_filter": [k for k in sorted(filter_template.keys())],
            "col_specs_filter": filter_template,
            "wanted_list_initial": [k for k in sorted(initial_template.keys())],
            "col_specs_initial": initial_template,
            "wanted_list": [k for k in sorted(stock_card_template.keys())],
            "col_specs": stock_card_template,
            "wanted_list_total": [k for k in sorted(stock_card_total.keys())],
            "col_specs_total": stock_card_total,
            "wanted_list_se_total": [k for k in sorted(stock_card_secundari.keys())],
            "col_specs_se_total": stock_card_secundari,
        }
        return [ws_params]

    def _stock_card_report(self, wb, ws, ws_params, data, objects, product):
        ws.set_portrait()
        ws.fit_to_pages(1, 0)
        ws.set_header(self.xls_headers["standard"])
        ws.set_footer(self.xls_footers["standard"])
        self._set_column_width(ws, ws_params)
        # Title
        row_pos = 0
        row_pos = self._write_ws_title(ws, row_pos, ws_params, True)
        # Filter Table
        product_lines = objects.results.filtered(
            lambda l: l.product_id == product and not l.is_initial
        )
        total_ave = 0.0
        counter = len(product_lines)
        for line in product_lines:
            nearest_standard_price = objects._get_nearest_standard_price(line.product_id, line.date)
            total_ave += nearest_standard_price
        final_average = total_ave/counter
        row_pos = self._write_line(
            ws,
            row_pos,
            ws_params,
            col_specs_section="header",
            default_format=self.format_theader_blue_center,
            col_specs="col_specs_filter",
            wanted_list="wanted_list_filter",
        )
        row_pos = self._write_line(
            ws,
            row_pos,
            ws_params,
            col_specs_section="data",
            render_space={
                "date_from": objects.date_from or "",
                "date_to": objects.date_to or "",
                "location": objects.location_id.display_name or "",
                "average": 0.0,
                "final_average": final_average
            },
            col_specs="col_specs_filter",
            wanted_list="wanted_list_filter",
        )
        row_pos += 1
        # Stock Card Table
        row_pos = self._write_line(
            ws,
            row_pos,
            ws_params,
            col_specs_section="header",
            default_format=self.format_theader_blue_center,
        )
        ws.freeze_panes(row_pos, 0)
        balance = objects._get_initial(
            objects.results.filtered(lambda l: l.product_id == product and l.is_initial)
        )
        row_pos = self._write_line(
            ws,
            row_pos,
            ws_params,
            col_specs_section="data",
            render_space={"balance": balance},
            col_specs="col_specs_initial",
            wanted_list="wanted_list_initial",
        )
        # product_lines = objects.results.filtered(
        #     lambda l: l.product_id == product and not l.is_initial
        # )
        total_entradas = 0.0
        total_salidas = 0.0
        total_balance = 0.0
        total_se_entradas = 0.0
        total_se_salidas = 0.0
        total_se_balance = 0.0
        for line in product_lines:
            balance += line.product_in - line.product_out
            nearest_standard_price = objects._get_nearest_standard_price(line.product_id, line.date)
            row_pos = self._write_line(
                ws,
                row_pos,
                ws_params,
                col_specs_section="data",
                render_space={
                    "date": line.date or "",
                    "reference": line.reference or "",
                    "nearest_standard_price": nearest_standard_price,
                    "input": line.product_in or 0,
                    "output": line.product_out or 0,
                    "balance": balance,
                },
                default_format=self.format_tcell_amount_right,
            )
            total_entradas += line.product_in or 0
            total_salidas += line.product_out or 0
            total_balance = balance
            total_se_entradas = product.uom_id._compute_quantity(total_entradas, product.sh_secondary_uom)
            total_se_salidas = product.uom_id._compute_quantity(total_salidas, product.sh_secondary_uom)
            total_se_balance = product.uom_id._compute_quantity(total_balance, product.sh_secondary_uom)
        row_pos = self._write_line(
            ws,
            row_pos,
            ws_params,
            col_specs_section="data",
            render_space={
                'total_entradas': total_entradas,
                'total_salidas': total_salidas,
                'total_balance': total_balance,
            },
            col_specs="col_specs_total",
            wanted_list="wanted_list_total",
        )
        row_pos = self._write_line(
            ws,
            row_pos,
            ws_params,
            col_specs_section="data",
            render_space={
                'total_se_entradas': total_se_entradas,
                'total_se_salidas': total_se_salidas,
                'total_se_balance': total_se_balance,
            },
            col_specs="col_specs_se_total",
            wanted_list="wanted_list_se_total",
        )

