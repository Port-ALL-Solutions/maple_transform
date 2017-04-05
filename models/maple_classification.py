# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

# modifier le contact (partner) de Odoo pour inclure sa région et son numéro FPAQ
class MapleClassLine(models.Model):
    _name = 'maple.classification.line'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    classification_id = fields.Many2one(
        comodel_name='maple.classification', 
        string='Classification Reference', 
        required=True, 
        ondelete='cascade', 
        index=True, 
        copy=False
        )
    
    quant_id = fields.Many2one(
        comodel_name='stock.quant', 
        string='Quant', 
        required=True, 
        index=True, 
        copy=False
        ) 

    acer_seal_no = fields.Char(
        string="Seal No.",
        help="Acer Seal Number",
        related='quant_id.acer_seal_no'
        )

    maple_seal_no = fields.Char(
        string="Seal No.",
        help="Maple Seal Number",
        related='quant_id.acer_seal_no'        
        )

    weight = fields.Float('Pounds')
    
    product_id = fields.Many2one(
        comodel_name='product.product', 
        string='Maple Product',
        )  

    producer_id = fields.Many2one(
        comodel_name='res.partner', 
        string='Producer',
        related='quant_id.producer' 
        )      
    
    producer_name = fields.Char(
        string='Producer',
        related='quant_id.producer.name' 
        )      
    
    sequence = fields.Integer(string='Sequence', default=10)


class MapleClassDoc(models.Model):
    _name = 'maple.classification'
    
    name = fields.Char(
        string='Doc Reference', 
        required=True, 
        copy=False, 
        readonly=True, 
        index=True,
        default=lambda self: _('New')
        )

    location_id = fields.Many2one(
        'stock.location', 
        'Classification Location',
        )
     
    state = fields.Selection(
        [   ('draft', 'Preparation'),
            ('done', 'Classify'),
            ('cancel', 'Cancelled'), ], 
        string='Status', 
        readonly=True, 
        copy=False, 
        index=True, 
        default='draft'
        )
    
    classification_date = fields.Datetime(
        string='Classification Date', 
        required=True, 
        readonly=True, 
        index=True, 
#        states={'draft': [('readonly', False)]}, 
        copy=False, 
        default=fields.Datetime.now
        )
    
    create_date = fields.Datetime(
        string='Creation Date', 
        readonly=True, 
        index=True, 
        help="Date on which classification is created."
        )

    note = fields.Text('Notes')
    
    classification_line = fields.One2many(
        comodel_name='maple.classification.line', 
        inverse_name='classification_id', 
        string='Classification Lines', 
        copy=True
        )
    
    
    
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('maple.classification') or 'New'
        result = super(MapleClassDoc, self).create(vals)
        return result
