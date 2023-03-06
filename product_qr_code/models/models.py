try:
    import qrcode
except ImportError:
    qrcode = None
try:
    import base64
except ImportError:
    base64 = None
from io import BytesIO

from odoo.addons.portal.controllers.portal import _build_url_w_params
from odoo.addons.http_routing.models.ir_http import slug
from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import UserError


class Products(models.Model):
    _inherit = 'product.product'

    qr = fields.Binary(string="QR Code")

    @api.model
    def create(self, vals):
        res = super(Products, self).create(vals)
        res.generate_qr()
        return res
        
    def get_product_url(self):
        params = {}
        if self.lot_ids:
            params['search'] = self.lot_ids[0].name
        return self.env['ir.config_parameter'].get_param('web.base.url') + _build_url_w_params("/shop/%s" % slug(self), params)

    @api.depends('lot_ids')
    def generate_qr(self):
        if qrcode and base64:
            url = self.get_product_url()
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(url)
            qr.make(fit=True)

            img = qr.make_image()
            temp = BytesIO()
            img.save(temp, format="PNG")
            qr_image = base64.b64encode(temp.getvalue())
            self.write({'qr': qr_image})
            return {
                'type': 'ir.actions.act_url',
                'url': str('/web/content/?model=product.product&field=qr&id='+str(self.id) + "&download=true&filename=" + self.name),
                'target': 'new',
                }
        else:
            if not qrcode:
                raise UserError(
                    _('Necessary Requirements To Run This Operation Is Not Satisfied: qrcode'))
            if not base64:
                raise UserError(
                    _('Necessary Requirements To Run This Operation Is Not Satisfied: base64'))

    def download_qr(self):
        return {
                'type': 'ir.actions.act_url',
                'url': str('/web/content/?model=product.product&field=qr&id='+str(self.id) + "&download=true&filename=" + self.name),
                'target': 'new',
        }


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    qr = fields.Binary(string="QR Code")

    def generate_qr(self):
        return {
                'type': 'ir.actions.act_url',
                'url': str('/web/content/?model=product.product&field=qr&id='+str(self.product_variant_id.id) + "&download=true&filename=" + self.product_variant_id.name),
                'target': 'new',
        }

    def download_qr(self):
        return {
                'type': 'ir.actions.act_url',
                'url': str('/web/content/?model=product.product&field=qr&id='+str(self.product_variant_id.id) + "&download=true&filename=" + self.product_variant_id.name),
                'target': 'new',
        }
