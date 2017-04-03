# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from datetime import date
from odoo.exceptions import UserError

class MapleTransform(models.TransientModel):
    _name = 'maple.transform_order'
    
    location_id = fields.Many2one(
        'stock.location', 
        'Classification Location',
        )
            
    def action_wizard_process_transform(self):
        #POST PROCESSING
        quant_obj = self.env['stock.quant']
        product_obj = self.env['product.product']
        location_obj = self.env['stock.location']
        
        inventory_obj = self.env['stock.inventory']
        doc_name = 'Classification ' + self.location_id.name + ' ' + date.today().strftime("%d/%m/%y") # une sequence serait bien
        inventory = inventory_obj.search([('name','=','doc_name')])
        if not inventory:
            inventory_line_obj = self.env['stock.inventory.line']           
            inventory_vals = {
                'name' : doc_name,  # Put better one there
                'location_id' : self.location_id.id,
                'filter' : 'none',   # Put better one there
                'state' : 'draft',
                }
            inventory = inventory_obj.create(inventory_vals)
        
        quants = quant_obj.search([('location_id','=',self.location_id.id)])               
        #Ok les boys, on a tous les quants du classement et un ajustement d'inventaire prêt. 
        
        for quant in quants:
            product = product_obj.search([('default_code','=',quant.product_code)])
            if product:
                inventory_line = inventory_line_obj.search([('inventory_id','=',inventory.id),('product_id','=',product.id)])
                if not inventory_line:
                    inventory_line_vals = {
                        'inventory_id' : inventory.id,
                        'product_id' : product.id,
                        'location_id' : self.location_id.id
                        }
                    inventory_line = inventory_line_obj.create(inventory_line_vals)
                new_qty = inventory_line.product_qty + quant.container_total_weight - quant.container_tar_weight
                inventory_line.write({'product_qty':new_qty})

  
        # on fini par post_inventory
#            product = product_obj.search([('default_code','=',quant.product_id.default_code)])
        