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
        # POST PROCESSING
        # Tous les quants sont dans le même localisation et devrait être valide
        quant_obj = self.env['stock.quant']
        location_obj = self.env['stock.location']
        classification_obj = self.env['maple.classification']
        classification_line_obj = self.env['maple.classification.line']
        product_obj = self.env['product.product']
        picking_obj = self.env['stock.picking']
        picking_type_obj = self.env['stock.picking.type']

        move_obj = self.env['stock.move']
        
        picking_type = picking_type_obj.search([('default_location_src_id','=',self.location_id.id)])        

        purchase_obj = self.env['purchase.order']
        purchase_line_obj = self.env['purchase.order.line']

        
        # OK on commence par ramasser tout le stock de la localisation, par producteur et par code de produit
        quants = quant_obj.search([('location_id','=',self.location_id.id),('product_code','!=',False)], order='producer,product_code')          
        
        # on crée un document et on le remplis (avec les quants pour l'instant)                
        classification_vals = {
                'name' : 'New',  # Puproduction_lot_obj.t better one there
                'location_id' : self.location_id.id,
                'state' : 'draft',
                }
                
        classification = classification_obj.create(classification_vals)
        
        active_producer = None
        
        # on boucle de les quaunts une premiere fois
        for quant in quants:
            # On trouve le produit résultant de la classification 
            product = product_obj.search([('default_code','=',quant.product_code)],limit=1)

            # On produit la ligne de résultat pour le quant
            classification_line_vals = {
                'classification_id' : classification.id,  # Put better one there
                'quant_id' : quant.id,
                'product_id': product.id,                
                'weight': quant.container_total_weight - quant.container_tar_weight,
                }
            classification_line = classification_line_obj.create(classification_line_vals)

            # Si c'est un nouveau producteur (ou le premier)            
            if quant.producer != active_producer:
                #Créer un Purchase Order
                purchase_vals = {
                    'partner_id':quant.producer.id,
                    'date_planned':date.today(),
                    'state':'purchase',
                    'location_id':quant.location_id.id,
                    
                }
                purchase_order = purchase_obj.create(purchase_vals)
                active_producer = quant.producer
            
            # Créer la ligne d'achat pour le quant
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
            quant.lot_id.received_name = quant.lot_id.name
            quant.lot_id.name = quant.maple_seal_no

        # FIN DE LA PREMIERE BOUCLE
        # Les produits ont été ajouté a des achats
        # Faut transformer les barils
        
        active_product = None        
        production = None
        
        quants = quant_obj.search([('location_id','=',self.location_id.id),('product_code','!=',False)], order='product_code')          
        for quant in quants:            
            if quant.product_code != active_product:
                if production:
                    production.write({
                        'product_qty' : qty_prod_bom })
                # on crée tout de suite un prod_order, on modifie la qté plus tard
                to_produce = self.env['product.product'].search([('default_code','=',quant.product_id.default_code [:1] + quant.product_code)])
                bom = self.env['mrp.bom'].search([('product_id','=',to_produce.id)])        
                
                production_vals = {                    
                    'product_id': to_produce.id,
                    'product_qty' : 1,
                    'product_uom_id' : to_produce.uom_id.id,
                    'Name' : "Transfo",
                    'location_src_id': quant.location_id.id,
                    'location_dest_id': quant.location_id.id,
                    'bom_id': bom.id
                }
                production = self.env['mrp.production'].create(production_vals)
                active_product = quant.product_code
                qty_prod_bom = quant.qty
            else :
                qty_prod_bom += quant.qty
            
        if production:
            production.write({
                'product_qty' : qty_prod_bom })
        
                



























        
#         active_location = None
#         active_product = None        
#         
#         
#         # achats terminés, passons au pickings
#         
#         # OK on commence par ramasser tout le stock de la localisation, par destination et par code de produit             
#         quants = quant_obj.search([('location_id','=',self.location_id.id)], order='location_dest_id,product_code')          
#         for quant in quants:
#              
#             # Si c'est un nouvelle destination (ou la premiere)
#             if quant.location_dest_id != active_location:
#                 #Crée un nouveau picking
#                 if active_location:
#                     picking.action_confirm()
#                     picking.action_assign()
#                     picking.set_pack_operation_lot_assign()
#                     
#                 picking_vals = {
#                     'origin': classification.name,
#                     'partner_id': False,
#                     'date_done': date.today(),
#                     'picking_type_id': picking_type.id,
#                     'move_type': 'direct',
# #                    'note': self.note or "",
#                     'location_id': quant.location_id.id,
#                     'location_dest_id': quant.location_dest_id.id,
#                 }
#                 picking = picking_obj.create(picking_vals)
#                 active_location = quant.location_dest_id
#                 #On remet active_product à None pour être sur des lignes
#                 active_product = None
#                 
#             # Si c'est un noveau produit (ou le premier du picking)                         
#             if quant.product_id != active_product:
#                 if not active_product:
#                     move_vals= {
#                         'picking_id': picking.id,
#                         'product_id': quant.product_id.id,
#                         'name': classification.name + "-" + quant.product_code,
#                         'product_uom_qty' : quant.qty,
#                         'product_uom' : quant.product_id.uom_id.id,
#                         'location_id': quant.location_id.id,
#                         'location_dest_id': quant.location_dest_id.id,
#                     }
#                     lots = []                
#                     move = move_obj.create(move_vals)
#                 move_product_qty = quant.qty
#                 active_product = quant.product_id
#             else:
#                 move_product_qty += quant.qty
# 
#         #faudrait ajouter un condition
#         picking.action_confirm()
#         picking.action_assign()
#         picking.set_pack_operation_lot_assign()
