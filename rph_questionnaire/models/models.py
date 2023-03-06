# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

YES_NO_SELECTION = [('yes', 'Yes'), ('no', 'No')]
HALAL_SELECTION = [('halal', 'Halal'), ('non-halal', 'Non-Halal')]

class RPHQuestionnaire(models.Model):
    _name = 'rph.questionnaire'
    _description = 'rph.questionnaire'

    name = fields.Char(string='Number', required=True, copy=False, default=lambda self: self.env['ir.sequence'].next_by_code('rph.questionnaire'))
    partner_id = fields.Many2one('res.partner', string='Contact', required=True)
    no_lot = fields.Char(string='Nomor Lot', copy=False)
    waktu_potong = fields.Date(string="Waktu Potong")
    waktu_kirim = fields.Date(string="Waktu Kirim")
    has_certificate = fields.Selection(YES_NO_SELECTION, required=True)
    certificate_no = fields.Char(string='No Sertifikat', copy=False)
    certificate_exp = fields.Date(string="Tanggal Expired")
    is_muslim = fields.Selection(YES_NO_SELECTION, string="Apakah penyembelih beragama Islam?")
    use_sharp_knife = fields.Selection(YES_NO_SELECTION, string="Apakah menggunakan pisau tajam dan sekali potong?")
    with_basmalah = fields.Selection(YES_NO_SELECTION, string="Apakah mengucap basmalah sebelum memotong?")
    correctly_cut = fields.Selection(YES_NO_SELECTION, string="Apakah pemotongan memutus saluran pernafasan dan dua urat leher?")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('process', 'In Process'),
        ('done', 'Done'),
    ], required=True, default='draft', string='Status',
        help="The 'Status' is used for approval process of questionnaire")
    is_halal = fields.Selection(HALAL_SELECTION, string="Halal?", copy=False)
    picking_id = fields.Many2one('stock.picking', string="Transfer")

    @api.model
    def create(self, vals):
        res = super(RPHQuestionnaire, self).create(vals)
        res.action_confirm()
        res.action_process()
        res.assign_partner()
        res.assign_lot()
        return res

    def action_confirm(self):
        for rec in self:
            rec.state = 'process'
    
    def action_process(self):
        for rec in self:
            if rec.has_certificate == 'yes' and rec.certificate_no and rec.certificate_exp:
                is_halal = True
            else:
                is_halal = rec.is_muslim == 'yes' and rec.use_sharp_knife == 'yes' and rec.with_basmalah == 'yes' and rec.correctly_cut == 'yes'
            if is_halal:
                rec.is_halal = 'halal'
            else:
                rec.is_halal = 'non-halal'
                
            rec.state = 'done'
            
    def assign_partner(self):
        for rec in self:
            if rec.partner_id:
                rec.partner_id._compute_rph_questionnaire_id()

    def assign_lot(self):
        for rec in self:
            _logger.info("rec.picking_id.move_ids_without_package = ")
            _logger.info(rec.picking_id.move_ids_without_package)
            if rec.picking_id and rec.picking_id.move_ids_without_package:
                for move in rec.picking_id.move_ids_without_package:
                    if move.move_line_ids:
                        move.move_line_ids[0].write({'lot_name': rec.no_lot, 'qty_done': 1})
                        # move._action_done()


class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    is_rph = fields.Boolean("Is RPH")
    rph_questionnaire_ids = fields.One2many('rph.questionnaire', 'partner_id', string='RPH Questionnaire', copy=False, store=True)
    rph_questionnaire_id = fields.Many2one('rph.questionnaire', string='RPH Questionnaire', compute='_compute_rph_questionnaire_id', store=True)

    @api.depends('rph_questionnaire_id')
    def _compute_rph_questionnaire_id(self):
        for p in self:
            p.rph_questionnaire_id = p.rph_questionnaire_ids[:1].id
