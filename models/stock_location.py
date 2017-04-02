# -*- coding: utf-8 -*-
from openerp import models, fields, api
from odoo.tools.yaml_tag import record_constructor
#from numpy.distutils.fcompiler import none

# modifier le contact (partner) de Odoo pour inclure sa région et son numéro FPAQ
class stockLocation(models.Model):
    _name = 'stock.location'
    _inherit = 'stock.location'

    kanban_color = fields.Integer(
        string="Color",
        compute='_compute_stock',
        )

    kanban_color_rules = fields.Integer(
        string="Color rules",
        compute='_compute_stock',
        )

    current_owner  = fields.Text(
        string='Owner',
        compute='_compute_stock',
        help="Default Owner",
        store=True
        )
       
    current_buyer  = fields.Text(
        string='Buyer',
        compute='_compute_stock',
        help="Default Buyer",
        store=True
        )
       
    current_rules = fields.Char(
        string='Rules',
        help="Product Rules. ",
        compute='_compute_stock',
        )    
        
    current_product = fields.Char(
        string='Product',
        compute='_compute_stock',
        help="Default Product",
        store=True
        )    

    maxItem = fields.Integer(
        string="Maximum capacity",
        help="The maximum count of product that can be put in that location. ")
    
    spaceLeft = fields.Integer(
        string="Product Space Left",
        help="The empty product space in that location. ")
    
    purchase_lines = fields.One2many(           
        comodel_name='purchase.order.line', 
        inverse_name='location_id',
        string="Purchases",
        help='Stock purchase planed for that location. ')
    
    qty_purchased  = fields.Float(
        string='Quantity Purchased',
        compute='_compute_qty_purchase',
        store=True
        )
    
    stock_lines = fields.One2many(           
        comodel_name='stock.quant', 
        inverse_name='location_id',
        string="Stock",
        help='Stock for that location. ')
    
    qty_stock  = fields.Float(
        string='Quantity Stock',
        compute='_compute_qty_stock',
        )
      
    @api.depends('purchase_lines')
    def _compute_qty_purchase(self):
        for record in self:
            qty = 0 
            for line in record.purchase_lines:
                if line.product_id.type == 'product':
                    qty += line.product_qty          
            record.qty_purchased = qty


  
    @api.depends('stock_lines','stock_lines.owner_id','stock_lines.qty')
    def _compute_stock(self):
        for record in self:
            qty = 0
            product = []
            owner = []
            buyer = []
            origin = []
            owner_txt = ""
            
            
            for line in record.stock_lines:
                if line.product_id.type == 'product':
                    
                    if line.owner_id.id not in owner:
                        owner.append(line.owner_id.id)
                        if line.owner_id.state_id.code not in origin:
                            origin.append(line.owner_id.state_id.code)
                    
                    if line.buyer.id not in buyer:
                        buyer.append(line.buyer.id)
                    
                    if line.product_id.id not in product:
                        product.append(line.product_id.id)                         
                    
                    qty += line.qty

            if len(origin) == 1:
                if origin[0] == 'QC':
                    record.kanban_color_rules = 6                    
                    record.current_rules = "Québec"
                else:
                    record.kanban_color_rules = 5
                    record.current_rules = "Hors Qc"
            elif len(origin) > 1: 
                # un seul buyer
                if 'QC' in origin:
                    record.kanban_color_rules = 2
                    record.current_rules = "Mixed"
                else:
                    record.kanban_color_rules = 5
                    record.current_rules = "Hors Qc"
                    
            else:
                record.kanban_color_rules = 0
                record.current_rules = ""


            if len(product) == 1:
                # un seul buyer
                record.current_product = record.stock_lines[0].product_id.default_code
            else:
                record.current_product = "MIXED"
                  
                  
                  
            if len(buyer) == 1:
                # un seul buyer
                record.current_buyer = record.stock_lines[0].buyer_code
                if record.stock_lines[0].buyer_code == "SE":
                    record.kanban_color = 4
                elif record.stock_lines[0].buyer_code == "LB":
                    record.kanban_color = 5

            else:
                record.kanban_color = 2
                record.current_buyer = "MIXED"
                

            if owner :                                      
                if len(owner) == 1:
                    #un seul proprio
                    record.current_owner = owner_txt
#                    record.current_owner = owner[0]
                else:
                    # pas juste une
                    record.current_owner = "Multiple Producer"

            else:
                #vide
                record.kanban_color = 0
            record.qty_stock = qty
  
    @api.multi
    def get_stock_quant_per_location(self):
        return self._get_action('stock_picking_from_stock_quants.act_quant_location_open')  
    
    @api.multi
    def _get_action(self, action_xmlid):
        # TDE TODO check to have one view + custo in methods
        action = self.env.ref(action_xmlid).read()[0]
        if self:
            action['display_name'] = self.display_name
        return action