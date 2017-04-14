# -*- coding: utf-8 -*-
from openerp import models, fields, api
from datetime import date

class StockPickingLot(models.Model):
    _inherit = 'stock.picking'

    @api.one
    def set_pack_operation_lot_assign(self):
        self.ensure_one()
        for order in self:
            for pack_operation in order.pack_operation_product_ids:
                qty_done = pack_operation.product_qty
                pack_operation.write({'qty_done': qty_done})
                for lots in pack_operation.pack_lot_ids:
                    qty_todo = lots.qty_todo
                    lots.write({'qty': qty_todo})

class ProductionLot(models.Model):
    _name = 'stock.production.lot'
    _inherit = ['stock.production.lot']
    
    received_name = fields.Char('Reception Label',help="Reception Label")
      
class stockQuant2(models.Model):
    _name = 'stock.quant'
    _inherit = ['stock.quant']

    
#    maple_product_id = fields.Many2one('product.product', 'Maple Product')
                
    def action_process_classification_python(self, cr, uid, ids, context=None):
        # Pre Processing      
        wizard_obj = self.env['maple.transform_order']           
        vals = { 'location_id': self[0].location_id.id }                   
        wizard_id = wizard_obj.create(vals)        
        
        return {
            'name': 'Process Classification',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'maple.transform_order',
            'res_id': wizard_id.id,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context,
        }
            
        



            
            