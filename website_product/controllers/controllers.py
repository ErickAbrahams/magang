# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers import main
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.portal.controllers.portal import CustomerPortal


class Website(main.WebsiteSale):
    
    def _prepare_product_values(self, product, category, search, **kwargs):
        res = super()._prepare_product_values(product, category, search, **kwargs)
        if res.get('product', False):
            product = res['product']
            move_line = False
            picking = False
            lot_ids = []
            if search:
                lot_ids = request.env['stock.production.lot'].sudo().search(
                    [('name', '=', search)]
                )
                print('22......')
                print(lot_ids)
            else:
                lot_ids = product.product_variant_ids.lot_ids
                print('27......')
                print(lot_ids)
            if not lot_ids:
                lot_ids = request.env['stock.production.lot'].sudo().search(
                    [('product_id', '=', product.id)]
                )
                print('32......')
                print(lot_ids)
            domain = [
                ('lot_id', 'in', lot_ids.ids),
                ('state', '=', 'done'),
            ]
            move_lines = request.env['stock.move.line'].sudo().search(domain, order='date desc')
            delivery_ids = move_lines.picking_id.ids
            if delivery_ids:
                picking = request.env['stock.picking'].sudo().browse(delivery_ids[0])
        res['picking'] = picking
        return res


CustomerPortal.OPTIONAL_BILLING_FIELDS.append('certificate_no')
CustomerPortal.OPTIONAL_BILLING_FIELDS.append('certificate_exp')
