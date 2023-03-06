# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    rph_partner_id = fields.Many2one('res.partner', string='RPH Contact')
    rph_questionnaire_id = fields.Many2one('rph.questionnaire', string='RPH Questionnaire')
