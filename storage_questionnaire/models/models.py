# -*- coding: utf-8 -*-

from odoo import models, fields, api

YES_NO_SELECTION = [('yes', 'Yes'), ('no', 'No')]
HALAL_SELECTION = [('halal', 'Halal'), ('non-halal', 'Non-Halal')]

class StorageQuestionnaire(models.Model):
    _name = 'storage.questionnaire'
    _description = 'storage.questionnaire'

    name = fields.Char(string='Number', required=True, copy=False, default=lambda self: self.env['ir.sequence'].next_by_code('storage.questionnaire'))
    partner_id = fields.Many2one('res.partner', string='Contact', required=True)
    no_lot = fields.Char(string='Nomor Lot', copy=False)
    waktu_disimpan = fields.Date(string="Waktu Disimpan")
    waktu_keluar = fields.Date(string="Waktu Daging Keluar")
    has_certificate = fields.Selection(YES_NO_SELECTION, required=True)
    certificate_no = fields.Char(string='No Sertifikat', copy=False)
    certificate_exp = fields.Date(string="Tanggal Expired")
    
    join_other_goods = fields.Selection(YES_NO_SELECTION, string="Digabung dengan bahan lain?", default=False)
    other_goods_is_halal = fields.Selection(YES_NO_SELECTION, string="Bahan lain memiliki kehalalan?", default=False)
    mix_with_other_goods = fields.Selection(YES_NO_SELECTION, string="Tercampur dengan bahan yang tidak halal?", default=False)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('process', 'In Process'),
        ('done', 'Done'),
    ], required=True, default='draft', string='Status',
        help="The 'Status' is used for approval process of questionnaire")
    is_halal = fields.Selection(HALAL_SELECTION, string="Halal?", copy=False)


    @api.model
    def create(self, vals):
        res = super(StorageQuestionnaire, self).create(vals)
        res.action_confirm()
        res.action_process()
        res.assign_partner()
        res.link_with_transfer()
        return res

    def action_confirm(self):
        for rec in self:
            rec.state = 'process'
    
    def action_process(self):
        for rec in self:
            if rec.has_certificate == 'yes' and rec.certificate_no and rec.certificate_exp:
                is_halal = True
            elif rec.join_other_goods == 'no':
                is_halal = True
            elif rec.other_goods_is_halal:
                is_halal = True
            else :
                is_halal = rec.mix_with_other_goods == 'no'
            if is_halal:
                rec.is_halal = 'halal'
            else:
                rec.is_halal = 'non-halal'
                
            rec.state = 'done'
    
    def assign_partner(self):
        for rec in self:
            if rec.partner_id:
                rec.partner_id._compute_storage_questionnaire_id()

    def link_with_transfer(self):
        StockProductionLot = self.env["stock.production.lot"].sudo()
        StockMoveLine = self.env["stock.move.line"].sudo()
        for rec in self:
            if rec.no_lot and rec.partner_id:
                lot_ids = StockProductionLot.search([('name', '=', rec.no_lot)])
                picking = False
                if lot_ids:
                    move_lines = StockMoveLine.search([('lot_id', 'in', lot_ids.ids)])
                    if move_lines:
                        picking = move_lines[0].picking_id
                if picking:
                    picking.storage_partner_id = rec.partner_id.id
                    picking.storage_questionnaire_id = rec.id

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    is_storage = fields.Boolean("Is Storage")
    storage_questionnaire_ids = fields.One2many('storage.questionnaire', 'partner_id', string='Storage Questionnaire', copy=False, store=True)
    storage_questionnaire_id = fields.Many2one('storage.questionnaire', string='Storage Questionnaire', compute='_compute_storage_questionnaire_id', store=True)

    @api.depends('storage_questionnaire_id')
    def _compute_storage_questionnaire_id(self):
        for p in self:
            p.storage_questionnaire_id = p.storage_questionnaire_ids[:1].id
            print("p.storage_questionnaire_ids = %s" % (p.storage_questionnaire_ids))
            print("p.storage_questionnaire_id = %s" % (p.storage_questionnaire_id))
