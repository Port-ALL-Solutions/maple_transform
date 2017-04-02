# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from datetime import date
from odoo.exceptions import UserError

class MapleTransform(models.TransientModel):
    _name = 'maple.transform_order'
    
    Location_id = fields.Many2one(
        'stock.location', 
        'Classification Location',
        )
            
    def action_wizard_process_transform(self):
        #POST PROCESSING
        quant_obj = self.env['stock.quant']
        location_obj = self.env['stock.location']
        
#        location_id = location_obj.search([('','','')])