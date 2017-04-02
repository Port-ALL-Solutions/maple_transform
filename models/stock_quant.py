# -*- coding: utf-8 -*-
from openerp import models, fields, api
from datetime import date


class stockQuant(models.Model):
    _name = 'stock.quant'
    _inherit = ['stock.quant']
    
    maple_product_id = fields.Many2one('product.product', 'Maple Product')
    


    def get_product_code_acer(self):

            # y a un scelé mais pas encore produit maple
            # donc on peux transformer, faut faire un match entre les propriétés
            # du quants et les produits vendants, en utilisant les champs/attibuts suivant
            # 1 = Bio/Pending/Régulier/NC
            # 2 = Grade
            # 3 = Brix
            # 4 = Flavor
            # 5 = Defaut
            # Quoi d'autre
            
            # on construit le nouveau code produit
        
        if self.product_id.default_code in ['BB','TB']:
            if self.owner.maple_bio:
                maple_product_code = 'B'
            else:
                maple_product_code = 'P'
            # Bio ou Pending
        else :
            maple_product_code = 'R' 
        
        maple_product_code += self.maple_grade
        
        if self.maple_grade in ['BB','TB']:
            if self.owner.maple_bio:
                maple_product_code = 'B'
            else:
                maple_product_code = 'P'
            # Bio ou Pending
        else :
            maple_product_code = 'R'
        return  maple_product_code

    
    def get_product_code_se(self):
        if self.product_id.default_code in ['BB','TB']:
            if self.owner.maple_bio:
                maple_product_code = 'B'
            else:
                maple_product_code = 'P'
            # Bio ou Pending
        else :
            maple_product_code = 'R' 
        
        maple_product_code += self.maple_grade
        
        if self.maple_grade in ['BB','TB']:
            if self.owner.maple_bio:
                maple_product_code = 'B'
            else:
                maple_product_code = 'P'
            # Bio ou Pending
        else :
            maple_product_code = 'R'
        return  maple_product_code
   
    
    def create_maple_product_acer(self):
        attibut_obj = self.env['product.atribute']
        attibut_value_obj = self.env['product.atribute.value']

        new_product_code = None
        if self.acer_seal_no and not self.maple_product_id:
            new_product_code = self.get_product_code_acer()
        elif self.maple_seal_no and not self.maple_product_id:
            new_product_code = self.get_product_code_se()
            
           
            
            
            
            