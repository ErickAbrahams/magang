# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProductProduct(models.Model):
    _inherit = "product.product"

    lot_ids = fields.One2many('stock.production.lot', 'product_id', string="Lot/Serial Number")
    picking_id = fields.Many2one('stock.picking', string='Transfer', compute='compute_stock_picking')

    def compute_stock_picking(self):
        for rec in self:
            domain = [
                ('lot_id', 'in', rec.lot_ids.ids),
                ('state', '=', 'done'),
            ]
            move_lines = self.env['stock.move.line'].search(domain, order='date desc')
            delivery_ids = move_lines.picking_id.ids
            if delivery_ids:
                rec.picking_id = delivery_ids[0]
            else:
                rec.picking_id = None


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model
    def _search_get_detail(self, website, order, options):
        res = super()._search_get_detail(website, order, options)
        res['search_fields'].append('product_variant_ids.lot_ids.name')
        res['mapping']['product_variant_ids.lot_ids.name'] = {'name': 'product_variant_ids.lot_ids.name', 'type': 'text', 'match': True}
        return res

    
