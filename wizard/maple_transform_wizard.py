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
        location_obj = self.env['stock.location']
        classification_obj = self.env['maple.classification']
        classification_line_obj = self.env['maple.classification.line']
        product_obj = self.env['product.product']
        picking_obj = self.env['stock.picking']
        picking_type_obj = self.env['stock.picking.type']
        
        picking_type = picking_type_obj.search([('default_location_src_id','=',self.location_id.id)])        

        purchase_obj = self.env['purchase.order']
        purchase_line_obj = self.env['purchase.order.line']

#        doc_name = 'Classification ' + self.location_id.name + ' ' + date.today().strftime("%d/%m/%y") # une sequence serait bien
#        inventory = inventory_obj.search([('name','=','doc_name')])
#        if not inventory:
#            inventory_line_obj = self.env['stock.inventory.line']           
#            inventory_vals = {
#                'name' : doc_name,  # Put better one there
#                'location_id' : self.location_id.id,
#                'filter' : 'none',   # Put better one there
#                'state' : 'draft',
#                }
#            inventory = inventory_obj.create(inventory_vals)
        
        quants = quant_obj.search([('location_id','=',self.location_id.id)], order='producer,product_code')          
        #Ok les boys, on a tous les quants du classement et un ajustement d'inventaire prêt. 
        # on crée un document et on le remplis (avec les quants pour l'instant)
        
        classification_vals = {
                'name' : 'New',  # Put better one there
                'location_id' : self.location_id.id,
                'state' : 'draft',
                }
                
        classification = classification_obj.create(classification_vals)
        
        active_producer = None
        
        for quant in quants:
            product = product_obj.search([('default_code','=',quant.product_code)],limit=1)

            classification_line_vals = {
                'classification_id' : classification.id,  # Put better one there
                'quant_id' : quant.id,
                'product_id': product.id,                
                'weight': quant.container_total_weight - quant.container_tar_weight,
                }
            classification_line = classification_line_obj.create(classification_line_vals)
            
            if quant.producer != active_producer:
                purchase_vals = {
                    'partner_id':quant.producer.id,
                    'date_planned':date.today(),
                    'state':'purchase',
                    'location_id':quant.location_id.id,
                    
                }
                purchase_order = purchase_obj.create(purchase_vals)
                active_producer = quant.producer
            
            purchase_line_vals = {
                'product_id':product.id,
                'product_qty': quant.container_total_weight - quant.container_tar_weight,
                'order_id':purchase_order.id,
                'name':purchase_order.name + quant.product_code,
                'product_uom':product.uom_id.id,
                'date_planned':date.today(),                
                'price_unit':product.price, # champ de prchase_order_line : champs de product_template                
                'location_id':quant.location_id.id,

            }           
                
            purchase_order_line = purchase_line_obj.create(purchase_line_vals)

        active_location = None
        active_product = None        
            
        quants = quant_obj.search([('location_id','=',self.location_id.id)], order='location_dest_id,product_code')          
        for quant in quants:
            
            if quant.location_dest_id != active_location:
                picking_vals = {
                    'origin': classification.name,
                    'partner_id': False,
                    'date_done': date.today(),
                    'picking_type_id': picking_type.id,
                    'move_type': 'direct',
#                    'note': self.note or "",
                    'location_id': quant.location_id.id,
                    'location_dest_id': quant.location_dest_id.id,
                }
                picking = picking_obj.create(picking_vals)
            
            if quant.product_id != active_product:
                if active_product:
                    move_vals= {
                        'picking_id': picking.id,
                        'product_id': quant.product_id.id,
                        'name': classification.name + "-" + quant.product_code,
                        'product_uom_qty' : move_product_qty,
                        'product_uom' : quant.product_id.uom_id.id,
                        'location_id': quant.location_id.id,
                        'location_dest_id': quant.location_dest_id.id,
                    }                
                    move = move_obj.create(move_vals)
                move_product_qty = quant.qty
                active_product = quant.product_id
            else:
                move_product_qty += quant.qty

            
            
            
            
            
#            if product:
#                inventory_line = inventory_line_obj.search([('inventory_id','=',inventory.id),('product_id','=',product.id)])
#                if not inventory_line:
#                    inventory_line_vals = {
#                        'inventory_id' : inventory.id,
#                        'product_id' : product.id,
#                        'location_id' : self.location_id.id
#                        }
#                    inventory_line = inventory_line_obj.create(inventory_line_vals)
#                new_qty = inventory_line.product_qty + quant.container_total_weight - quant.container_tar_weight
#                inventory_line.write({'product_qty':new_qty})
# on fini par post_inventory
#            product = product_obj.search([('default_code','=',quant.product_id.default_code)])
        