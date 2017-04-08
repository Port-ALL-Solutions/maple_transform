# -*- coding: utf-8 -*-
from openerp import models, fields, api
from datetime import date

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
            
        



            
            