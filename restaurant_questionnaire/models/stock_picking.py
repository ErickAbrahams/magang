# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    restaurant_partner_id = fields.Many2one('res.partner', string='Restaurant Contact')
    restaurant_questionnaire_id = fields.Many2one('restaurant.questionnaire', string='Restaurant Questionnaire')
