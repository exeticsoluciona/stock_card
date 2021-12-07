# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields, api, _


class sh_stock_move(models.Model):
    _inherit = "stock.move"
    
    sh_sec_qty = fields.Float("Secondary Qty", digits='Product Unit of Measure', store=True, copy=False)
    sh_sec_done_qty = fields.Float("Secondary Done Qty", digits='Product Unit of Measure', store=True, copy=False)
    sh_sec_uom = fields.Many2one("uom.uom", 'Secondary UOM', related="product_id.sh_secondary_uom", store=True, copy=False)
    sh_is_secondary_unit = fields.Boolean("Related Sec Uni", related="product_id.sh_is_secondary_unit", store=True, copy=False)

    @api.onchange('quantity_done')
    def onchange_product_uom_done_qty_sh(self):
        if self and self.sh_is_secondary_unit == True and self.sh_sec_uom:
            self.sh_sec_done_qty = self.product_uom._compute_quantity(self.quantity_done, self.sh_sec_uom)

#    @api.onchange('sh_sec_done_qty')
#    def onchange_sh_sec_done_qty_sh(self):
#        if self and self.sh_is_secondary_unit == True and self.product_uom:
#            self.quantity_done = self.sh_sec_uom._compute_quantity(self.sh_sec_done_qty, self.product_uom)
            
    @api.onchange('product_uom_qty', 'product_uom')
    def onchange_product_uom_qty_sh(self):
        if self.sh_is_secondary_unit == True and self.sh_sec_uom:
            self.sh_sec_qty = self.product_uom._compute_quantity(self.product_uom_qty, self.sh_sec_uom)

#    @api.onchange('sh_sec_qty', 'sh_sec_uom')
#    def onchange_sh_sec_qty_sh(self):
#        if self and self.sh_is_secondary_unit == True and self.product_uom:
#            self.product_uom_qty = self.sh_sec_uom._compute_quantity(self.sh_sec_qty, self.product_uom)

    @api.model
    def create(self, vals):
        res = super(sh_stock_move, self).create(vals)
        if res.sale_line_id and res.sale_line_id.sh_is_secondary_unit == True and res.sale_line_id.sh_sec_uom:
            res.update({'sh_sec_uom':res.sale_line_id.sh_sec_uom.id, 'sh_sec_qty':res.sale_line_id.sh_sec_qty})
        elif res.purchase_line_id and res.purchase_line_id.sh_is_secondary_unit == True and res.purchase_line_id.sh_sec_uom:
            res.update({'sh_sec_uom':res.purchase_line_id.sh_sec_uom.id, 'sh_sec_qty':res.purchase_line_id.sh_sec_qty})
        return res

    
class sh_stock_move_line(models.Model):
    _inherit = "stock.move.line"
    
    sh_sec_qty = fields.Float("Secondary Qty", digits='Product Unit of Measure')
    sh_sec_uom = fields.Many2one("uom.uom", 'Secondary UOM', related="move_id.sh_sec_uom")
    sh_is_secondary_unit = fields.Boolean("Related Sec Uni", related="move_id.product_id.sh_is_secondary_unit")
    
    @api.onchange('qty_done')
    def onchange_product_uom_done_qty_sh_move_line(self):
        if self and self.sh_is_secondary_unit == True and self.sh_sec_uom:
            self.sh_sec_qty = self.product_uom_id._compute_quantity(self.qty_done, self.sh_sec_uom)
            self.move_id.sh_sec_done_qty = self.product_uom_id._compute_quantity(self.qty_done, self.move_id.sh_sec_uom)

#    @api.onchange('sh_sec_qty')
#    def onchange_product_sec_done_qty_sh_move_line(self):
#        if self and self.sh_is_secondary_unit == True and self.sh_sec_uom:
#            self.qty_done = self.sh_sec_uom._compute_quantity(self.sh_sec_qty, self.product_uom_id)
#            self.move_id.quantity_done = self.sh_sec_qty

            
class sh_stock_immediate_transfer(models.TransientModel):
    _inherit = 'stock.immediate.transfer'
    
    def process(self):
        res = super(sh_stock_immediate_transfer, self).process()
        for picking_ids in self.pick_ids:
            for moves in picking_ids.move_ids_without_package:
                if moves.sh_sec_uom:
                    moves.sh_sec_done_qty = moves.product_uom._compute_quantity(moves.product_uom_qty, moves.sh_sec_uom)
                for move_lines in moves.move_line_ids:
                    if move_lines.sh_sec_uom:
                        move_lines.sh_sec_qty = move_lines.product_uom_id._compute_quantity(move_lines.qty_done, moves.sh_sec_uom)
        return res

