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
#            product = product_obj.search([('default_code','=',quant.product_code)])
            maple_product_code = ""            

            if quant.maple_grade:            
                maple_product_code += quant.product_id.default_code[1] 
                maple_product_code += quant.maple_grade
                if not quant.maple_flavor and not quant.maple_flaw:
                    maple_product_code += '--'
                else:
                    if len(quant.maple_flavor) == 2:
                        maple_product_code += quant.maple_flavor[1]
                    elif len(quant.maple_flavor) > 2:
                        maple_product_code += "R"
                if quant.maple_flaw:
                    maple_product_code += quant.maple_flaw
                else:
                    maple_product_code += "0"
                print maple_product_code
            else:
                print "pas grade"    
            

            if len(maple_product_code) == 5:
                self.product_code = maple_product_code    
        # on fini par post_inventory
            product = product_obj.search([('default_code','=',quant.product_id.default_code)])
        