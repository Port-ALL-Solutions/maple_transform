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

    def complete_produce_product(self, consumed_quants):
        quant_obj = self.env['stock.quant']

        to_produce = self.env['product.product'].search([('default_code','=',consumed_quants[0].product_id.default_code [:1] + consumed_quants[0].product_code)])
        bom = self.env['mrp.bom'].search([('product_id','=',to_produce.id)])        
                
        production_vals = {                    
            'product_id': to_produce.id,
            'product_qty' : len(consumed_quants),
            'product_uom_id' : to_produce.uom_id.id,
#                    'name' : "Transfo",
            'location_src_id': consumed_quants[0].location_id.id,
            'location_dest_id': consumed_quants[0].location_id.id,
            'bom_id': bom.id
        }
        production = self.env['mrp.production'].create(production_vals)
        production.action_assign()


        
        move_lots = self.env['stock.move.lots']
        lots = self.env['stock.production.lot']

        produce_move = production.move_finished_ids.filtered(lambda x: x.product_id == to_produce and x.state not in ('done', 'cancel'))
        consume_move = production.move_raw_ids.filtered(lambda x: x.state not in ('done', 'cancel'))

        consume_move.do_unreserve()
        consume_qty = 0
        for quant in consumed_quants:              
#            quant_tpl = quant_obj.quants_get_preferred_domain(1, consume_move, lot_id=quant.lot_id.id)
            quant.quants_reserve([(quant,1.0)], consume_move)
            consume_qty += 1
            lot = lots.create({                 
                'product_id': produce_move.product_id.id,
                'name': quant.maple_seal_no })
            
            vals = {
              'move_id': produce_move.id,
              'product_id': produce_move.product_id.id,
              'production_id': production.id,
              'quantity': 1.0,
              'quantity_done': 1.0,
              'lot_id': lot.id,
            }
            move_lots.create(vals)
        

            
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
                    'date_planned': date.today(),
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
#            quant.lot_id.received_name = quant.lot_id.name
#            quant.lot_id.name = quant.maple_seal_no

        # FIN DE LA PREMIERE BOUCLE
        # Les produits ont été ajouté a des achats
        # Faut transformer les barils
        
        active_product = None        
        production = None
        consumed = []
        
        quants = quant_obj.search([('location_id','=',self.location_id.id),('product_code','!=',False)], order='product_code')          
        for quant in quants:            
            if quant.product_code == active_product:
                consumed.append(quant)
            else:
                if active_product:
                    self.complete_produce_product(consumed)    
                active_product = quant.product_code
                consumed = []
                consumed.append(quant)
        
        if consumed :
            self.complete_produce_product(consumed)    
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
#                 if production:
#                     self.complete_produce_product(production, prod_lots)
#                 
#                 to_produce = self.env['product.product'].search([('default_code','=',quant.product_id.default_code [:1] + quant.product_code)])
#                 bom = self.env['mrp.bom'].search([('product_id','=',to_produce.id)])        
#                 
#                 production_vals = {                    
#                     'product_id': to_produce.id,
#                     'product_qty' : 1,
#                     'product_uom_id' : to_produce.uom_id.id,
# #                    'name' : "Transfo",
#                     'location_src_id': quant.location_id.id,
#                     'location_dest_id': quant.location_id.id,
#                     'bom_id': bom.id
#                 }
#                 production = self.env['mrp.production'].create(production_vals)
#                 active_product = quant.product_code
# 
#                 qty_prod_bom = quant.qty
#                 prod_lots = []
#                 prod_lots.append(quant.id)
#             
#             else :
#                 qty_prod_bom += quant.qty
#                 prod_lots.append(quant.id)
#             
#         if production:
#             self.complete_produce_product(production, prod_lots)
        
                



























        
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
