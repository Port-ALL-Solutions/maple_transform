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

    def create_picking_for_location(self, location_id):
        # On ramasse le type de picking depuis sa source par défaut
        picking_type = self.env['stock.picking.type'].search([('default_location_src_id','=',location_id)])          

        # Faut faire un picking par destination, un move par type de roduit par destination avec la quantité                     
        # OK on commence par ramasser tout le stock de la localisation, par destination et par code de produit
        quants = self.env['stock.quant'].search([('location_id','=',location_id)], order='location_dest_id,product_id')
              
        # on boucle par destination
        for destination in quants.mapped('location_dest_id'):
            # on filtre les quants pour la destination
            quants_dest =  quants.filtered(lambda r: r.location_dest_id == destination)
            # on crée le picking
            picking_vals = {
#                    'origin': classification.name,
                'partner_id': False,
                'date_done': date.today(),
                'picking_type_id': picking_type.id,
                'move_type': 'direct',
                'location_id': location_id,
                'location_dest_id': destination.id,
            }
            picking = self.env['stock.picking'].create(picking_vals)
            # on boucle ensuite par produit
            for product in quants_dest.mapped('product_id'):
                 # on filtre les quants par le produit en plus de destination
                quants_prod = quants_dest.filtered(lambda r: r.product_id == product)            
                # on crée le move
                move_vals= {
                    'picking_id': picking.id,
                    'product_id': product.id,
                    'name': picking.name + "-" + product.default_code,
                    'product_uom_qty' : len(quants_prod),
                    'product_uom' : product.uom_id.id,
                    'location_id': location_id,
                    'location_dest_id': destination.id,
                }
                move = self.env['stock.move'].create(move_vals)

            # On finalise le tout et laisse le soin a Odoo de faire les Lots (enfin)    
            picking.action_confirm()
            picking.action_assign()
            picking.set_pack_operation_lot_assign()


    def complete_produce_product(self, quants):
        # On regarde qu'est ce qu'on a a produire en calculant le produit résultnant
        to_produce_list = list(set(quants.mapped(lambda r: r.product_id.default_code[:1] + r.product_code)))
        # Récupération des produits correspondant 
        to_produce = self.env['product.product'].search([('default_code','in',to_produce_list)])        
        
        # On boucle dans les produits pour produire les documents
        productions = []
        for product in to_produce:
            # Récupération du bill of material correspondans au produit
            bom = self.env['mrp.bom'].search([('product_id','=',product.default_code)])
                
            # On filtre les quants
            quants_per_product = quants.filtered(lambda x: x.product_id.default_code == product.default_code[:2] and x.product_code == product.default_code[1:])

            production_vals = {                    
                'product_id': product.id,
                'product_qty' : len(quants_per_product),
                'product_uom_id' : product.uom_id.id,
                'location_src_id': quants[0].location_id.id,
                'location_dest_id': quants[0].location_id.id,
                'bom_id': bom.id
            }
    
            production = self.env['mrp.production'].create(production_vals)
            production.action_assign()
            productions.append(production)
            produce_move = production.move_finished_ids.filtered(lambda x: x.product_id == product and x.state not in ('done', 'cancel'))
            consume_move = production.move_raw_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
            consume_lots = consume_move.move_lot_ids

            consume_move.do_unreserve()
            consume_qty = 0
           
            for quant in quants_per_product:              
                quant.quants_reserve([(quant,1.0)], consume_move)
                consume_qty += 1
                lot = self.env['stock.production.lot'].create({                 
                    'product_id': produce_move.product_id.id,
                    'name': quant.maple_seal_no })
                
                consume_move.create_lots()
                for consumed_lot in consume_move.active_move_lot_ids:
                    consumed_lot.write({'quantity_done' : 1.})
                
                vals = {
                  'move_id': produce_move.id,
                  'product_id': produce_move.product_id.id,
                  'production_id': production.id,
                  'quantity': 1.0,
                  'quantity_done': 1.0,
                  'lot_id': lot.id,
                }
                self.env['stock.move.lots'].create(vals)
        
        for production in productions: 
            production.button_mark_done()

            for move in production.move_finished_ids:
                for produce_lot in move.active_move_lot_ids:
                    for quant in produce_lot.lot_id.quant_ids:
                        used_quant = quants.filtered(lambda x: x.maple_seal_no == quant.lot_id.name)
#                        used_quant = self.env['stock.quant'].search([('maple_seal_no','=',quant.lot_id.name)])
                        quant.write(    {   
                            'consumed_quant_ids':  [(6, 0, [used_quant.id])],
                            'container_serial' : used_quant.container_serial,
                            'container_ownership' : used_quant.container_ownership,
                            'container_state' : used_quant.container_state.id,                 
                            'container_total_weight' : used_quant.container_total_weight,
                            'tmp_tare' : used_quant.tmp_tare,
                            'tmp_material' : used_quant.tmp_material.id,
                            'tmp_owner' : used_quant.tmp_owner.id,
                            'maple_net_weight' : used_quant.maple_net_weight,                                        
                            'controler' : used_quant.controler.id,
                            'acer_seal_no' : used_quant.acer_seal_no,
                            'maple_seal_no' : used_quant.maple_seal_no,                 
                            'maple_light' : used_quant.maple_light,
                            'maple_grade' : used_quant.maple_grade,
                            'maple_brix' : used_quant.maple_brix,                 
                            'maple_flavor' : used_quant.maple_flavor.id,
                            'maple_flaw' : used_quant.maple_flaw.id,
                            'maple_adjust_weight' : used_quant.maple_adjust_weight,                 
                            'maple_adjust_price' : used_quant.maple_adjust_price,                 
                            'location_dest_id' : used_quant.location_dest_id.id,                 
                            'maple_producer' : used_quant.maple_producer,
                            })
                        used_quant.write(    {   
                            'produced_quant_ids':  [(6, 0, [quant.id])],
                        })
            

    def create_purchase_from_quants(self, quants):
        for producer in quants.mapped('producer'):
            quants_producer = quants.filtered(lambda r: r.producer == producer)

            purchase_vals = {
                    'partner_id':producer.id,
                    'date_planned': date.today(),
                    'state':'purchase',
                    'location_id':self.location_id.id,
                    
                }
            purchase_order = self.env['purchase.order'].create(purchase_vals)
            for product_code in quants_producer.mapped('product_code'):
                product = self.env['product.product'].search([('default_code','=',product_code)])
                for quant in quants_producer.filtered(lambda r: r.product_code == product_code):
                    purchase_line_vals = {
                        'product_id':product.id,
                        'product_qty': quant.container_total_weight - quant.container_tar_weight,
                        'order_id': purchase_order.id,
                        'name': purchase_order.name + quant.product_code,
                        'product_uom': product.uom_id.id,
                        'date_planned': date.today(),                
                        'price_unit': product.price, # champ de prchase_order_line : champs de product_template                
                        'location_id': quant.location_id.id,
        
                        }                           
                    purchase_order_line = self.env['purchase.order.line'].create(purchase_line_vals)

    def create_classification_from_quants(self, quants):
        for producer in quants.mapped('producer'):
            quants_producer = quants.filtered(lambda r: r.producer == producer)

            purchase_vals = {
                    'partner_id':quant.producer.id,
                    'date_planned': date.today(),
                    'state':'purchase',
                    'location_id':quant.location_id.id,
                    
                }
            purchase_order = self.env['purchase.order'].create(purchase_vals)
    
            for product in quants_producer.mapped(product_id):
                for quant in quants_producer.filtered(lambda r: r.product_id == product):
                    purchase_line_vals = {
                        'product_id':product.id,
                        'product_qty': quant.container_total_weight - quant.container_tar_weight,
                        'order_id': purchase_order.id,
                        'name': purchase_order.name + quant.product_code,
                        'product_uom': product.uom_id.id,
                        'date_planned': date.today(),                
                        'price_unit': product.price, # champ de prchase_order_line : champs de product_template                
                        'location_id': quant.location_id.id,
        
                        }                           
                    purchase_order_line = self.env['purchase.order.line'].create(purchase_line_vals)

        # on crée un document et on le remplis (avec les quants pour l'instant)                
#         classification_vals = {
#                 'name' : 'New',  # Puproduction_lot_obj.t better one there
#                 'location_id' : self.location_id.id,
#                 'state' : 'draft',
#                 }
#                 
#         classification = self.env['maple.classification'].create(classification_vals)
#         
#         active_producer = None
#         
#         # on boucle de les quaunts une premiere fois
#         for quant in quants:
#             # On trouve le produit résultant de la classification 
#             product = self.env['product.product'].search([('default_code','=',quant.product_code)],limit=1)
# 
#             # On produit la ligne de résultat pour le quant
#             classification_line_vals = {
#                 'classification_id' : classification.id,  # Put better one there
#                 'quant_id' : quant.id,
#                 'product_id': product.id,                
#                 'weight': quant.container_total_weight - quant.container_tar_weight,
#                 }
#             classification_line = self.env['maple.classification.line'].create(classification_line_vals)
# 

            
    def action_wizard_process_transform(self):
        # POST PROCESSING
        # Tous les quants sont dans le même localisation et devrait être valide               
        # OK on commence par ramasser tout le stock de la localisation, ayant un product_code, trier par producteur et par code de produit
        quants = self.env['stock.quant'].search([('location_id','=',self.location_id.id),('product_code','!=',False)], order='product_id, product_code')
#        to_produce_list = quants.mapped(lambda r: r.product_id.default_code[:1] + r.product_code)
        self.complete_produce_product(quants)
        
#        quants = self.env['stock.quant'].search([('location_id','=',self.location_id.id)], order='product_id')
        self.create_purchase_from_quants(quants)
        self.create_picking_for_location(self.location_id.id)    
