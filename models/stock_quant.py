# -*- coding: utf-8 -*-
from openerp import models, fields, api
from datetime import date


class stockQuant2(models.Model):
    _name = 'stock.quant'
    _inherit = ['stock.quant']
    
#    maple_product_id = fields.Many2one('product.product', 'Maple Product')
                
    def action_process_classification_python(self, cr, uid, ids, context=None):
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
            
        



            
            