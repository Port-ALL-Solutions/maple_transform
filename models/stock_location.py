# -*- coding: utf-8 -*-
from openerp import models, fields, api
from odoo.tools.yaml_tag import record_constructor
#from numpy.distutils.fcompiler import none

# modifier le contact (partner) de Odoo pour inclure sa région et son numéro FPAQ
class stockLocation(models.Model):
    _name = 'stock.location'
    _inherit = 'stock.location'

    @api.one
    def process_classification(self):
#        quant_obj = self.env['stock.quant']
#        attibut_value_obj = self.env['product.atribute.value']
#        quants = quant_obj.search([('location_id','=',self.id)])
#        for quant in quants:
#            quant.create_maple_product()
        return {
            'name': 'Process Classification',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'maple.classification_order',
#            'res_id': wizard_id.id,
            'type': 'ir.actions.act_window',
            'target': 'new',
#            'context': context,
        }