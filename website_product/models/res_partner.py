# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    certificate_no = fields.Char(string='Halal Certificate')
    certificate_exp = fields.Date(string='Certificate Exp Date')
