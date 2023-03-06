# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers import portal

class CustomerPortal(portal.CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super()._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        values['is_rph'] = partner.is_rph
        return values

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id

        RPHQuestionnaire = request.env['rph.questionnaire']
        if 'rph_questionnaire_state' in counters:
            questionnaire = RPHQuestionnaire.search(self._prepare_questionnaire_domain(partner), limit=1) \
                if RPHQuestionnaire.check_access_rights('read', raise_exception=False) else False
            questionnaire_state = questionnaire.state or False
            if questionnaire_state == 'draft':
                questionnaire_state = 'Dalam Proses'
            elif questionnaire_state == 'process':
                questionnaire_state = 'Dalam Proses'
            elif questionnaire_state == 'done':
                questionnaire_state = 'Selesai'
            else:
                questionnaire_state = 'Ajukan'
            values['rph_questionnaire_state'] = questionnaire_state

        return values

    def _prepare_questionnaire_domain(self, partner):
        return [
            ('partner_id', 'in', [partner.id]),
            ('state', 'in', ['draft', 'process', 'done'])
        ]

    @http.route(['/my/rph_questionnaire', '/my/rph_questionnaire/<int:quest_id>'], type='http', auth="user", website=True)
    def portal_rph_questionnaire(self, quest_id=None, date_begin=None, date_end=None, sortby=None, **kw):
        RPHQuestionnaire = request.env['rph.questionnaire']
        partner = request.env.user.partner_id

        if quest_id:
            questionnaire = RPHQuestionnaire.browse(quest_id)
            if not questionnaire.exists():
                return request.render("rph_questionnaire.portal_view_rph_questionnaire_not_found")    
            return request.render("rph_questionnaire.portal_view_rph_questionnaire", {
                    'questionnaire': questionnaire
                })
        else:
            questionnaire = RPHQuestionnaire.search(self._prepare_questionnaire_domain(partner), limit=1, order='write_date desc') \
                    if RPHQuestionnaire.check_access_rights('read', raise_exception=False) else False
            return request.render("rph_questionnaire.portal_my_rph_questionnaire", {
                    'questionnaire': questionnaire
                })

    @http.route(['/my/questionnaire/rph/picking/<int:picking_id>'], type='http', auth="user", website=True)
    def portal_new_rph_questionnaire_with_picking(self, picking_id, **kw):
        StockPicking = request.env['stock.picking'].sudo()
        picking = StockPicking.browse(picking_id)
        if picking.exists():
            return request.render("rph_questionnaire.portal_new_rph_questionnaire_with_picking", {
            "picking": picking
            })
        return request.render("rph_questionnaire.portal_new_rph_questionnaire_picking_not_found")

    @http.route(['/my/rph_transfer'], type='http', auth="user", website=True)
    def rph_transfer(self, **kw):
        picking_domain = [
            ('rph_partner_id', '=', request.env.user.partner_id.id),
            ('state', '=', 'assigned')
            ]
        picking_list = request.env['stock.picking'].sudo().search(picking_domain)
        return request.render("rph_questionnaire.portal_rph_transfer", {'picking_list': picking_list})


    @http.route(['/my/new_rph_questionnaire/<int:picking_id>'], type='http', auth="user", website=True)
    def portal_new_rph_questionnaire(self, picking_id, **kw):
        StockPicking = request.env['stock.picking'].sudo()
        picking = StockPicking.browse(picking_id)
        if not picking.exists():
            return request.render("rph_questionnaire.portal_new_rph_questionnaire_picking_not_found")

        no_lot = kw.get('no_lot') or None
        waktu_potong = kw.get('waktu_potong') or None
        waktu_kirim = kw.get('waktu_kirim') or None
        has_certificate = kw.get('has_certificate') or None
        certificate_no = kw.get('certificate_no') or None
        certificate_exp = kw.get('certificate_exp') or None
        is_muslim = kw.get('is_muslim') or None
        use_sharp_knife = kw.get('use_sharp_knife') or None
        with_basmalah = kw.get('with_basmalah') or None
        correctly_cut = kw.get('correctly_cut') or None
        input_data = {
            'no_lot': no_lot,
            'waktu_potong': waktu_potong,
            'waktu_kirim': waktu_kirim,
            'has_certificate': has_certificate,
            'certificate_no': certificate_no,
            'certificate_exp': certificate_exp,
            'is_muslim': is_muslim,
            'use_sharp_knife': use_sharp_knife,
            'with_basmalah': with_basmalah,
            'correctly_cut': correctly_cut,
        }
        show = None
        apply = kw.get('apply') or False
        if not no_lot:
            show = 'no_lot'
        if not show:
            if not waktu_potong:
                show = 'waktu_potong'
        if not show:
            if not waktu_kirim:
                show = 'waktu_kirim'
        if not show:
            if not has_certificate:
                show = 'has_certificate'
            elif has_certificate == 'yes':
                show = 'certificate_no'
            else:
                if not is_muslim:
                    show = 'is_muslim'
                elif is_muslim == 'no':
                    apply = True
        if not show:
            if not use_sharp_knife:
                show = 'use_sharp_knife'
            elif use_sharp_knife == 'no':
                apply = True
        if not show:
            if not with_basmalah:
                show = 'with_basmalah'
            elif with_basmalah == 'no':
                apply = True
            elif not correctly_cut:
                show = 'correctly_cut'
            else:
                apply = True

        if apply:
            RPHQuestionnaire = request.env['rph.questionnaire'].sudo()
            vals = {
                'no_lot': no_lot,
                'waktu_potong': waktu_potong,
                'waktu_kirim': waktu_kirim,
                'partner_id': request.env.user.partner_id.id,
                'has_certificate': has_certificate,
                'certificate_no': certificate_no,
                'certificate_exp': certificate_exp,
                'is_muslim': is_muslim,
                'use_sharp_knife': use_sharp_knife,
                'with_basmalah': with_basmalah,
                'correctly_cut': correctly_cut,
                'picking_id': picking.id
            }
            rec = RPHQuestionnaire.create(vals)
            picking.write({
                'rph_questionnaire_id': rec.id
                })
            return request.render("rph_questionnaire.portal_new_rph_questionnaire_success", {'rec': rec})
        return request.render("rph_questionnaire.portal_new_rph_questionnaire", 
            {'data': input_data, 'show': show, 'picking': picking})