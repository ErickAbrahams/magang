# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers import portal

class CustomerPortal(portal.CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super()._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        values['is_transport'] = partner.is_transport
        return values

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id

        TransportQuestionnaire = request.env['transport.questionnaire']
        if 'transport_questionnaire_state' in counters:
            questionnaire = TransportQuestionnaire.search(self._prepare_questionnaire_domain(partner), limit=1) \
                if TransportQuestionnaire.check_access_rights('read', raise_exception=False) else False
            
            questionnaire_state = False
            if questionnaire:
                questionnaire_state = questionnaire.state or False
            if questionnaire_state == 'draft':
                questionnaire_state = 'Dalam Proses'
            elif questionnaire_state == 'process':
                questionnaire_state = 'Dalam Proses'
            elif questionnaire_state == 'done':
                questionnaire_state = 'Selesai'
            else:
                questionnaire_state = 'Ajukan'
            values['transport_questionnaire_state'] = questionnaire_state

        return values

    def _prepare_questionnaire_domain(self, partner):
        return [
            ('partner_id', '=', [partner.id]),
            ('state', 'in', ['draft', 'process', 'done'])
        ]

    @http.route(['/my/transport_questionnaire', '/my/transport_questionnaire/<int:quest_id>'], type='http', auth="user", website=True)
    def portal_transport_questionnaire(self, quest_id=None, date_begin=None, date_end=None, sortby=None, **kw):
        TransportQuestionnaire = request.env['transport.questionnaire']
        partner = request.env.user.partner_id

        if quest_id:
            questionnaire = TransportQuestionnaire.browse(quest_id)
            return request.render("transport_questionnaire.portal_view_transport_questionnaire", {
                    'questionnaire': questionnaire
                })
        else:
            questionnaire = TransportQuestionnaire.search(self._prepare_questionnaire_domain(partner), limit=1, order='write_date desc') \
                    if TransportQuestionnaire.check_access_rights('read', raise_exception=False) else False
            return request.render("transport_questionnaire.portal_my_transport_questionnaire", {
                    'questionnaire': questionnaire
                })

    @http.route(['/my/new_transport_questionnaire'], type='http', auth="user", website=True)
    def portal_new_transport_questionnaire(self, **kw):
        no_lot = kw.get('no_lot') or None
        waktu_berangkat = kw.get('waktu_berangkat') or None
        waktu_sampai = kw.get('waktu_sampai') or None
        has_certificate = kw.get('has_certificate') or None
        certificate_no = kw.get('certificate_no') or None
        certificate_exp = kw.get('certificate_exp') or None
        join_other_goods = kw.get('join_other_goods') or None
        other_goods_is_halal = kw.get('other_goods_is_halal') or None
        mix_with_other_goods = kw.get('mix_with_other_goods') or None
        input_data = {
            'no_lot': no_lot,
            'waktu_berangkat': waktu_berangkat,
            'waktu_sampai': waktu_sampai,
            'has_certificate': has_certificate,
            'certificate_no': certificate_no,
            'certificate_exp': certificate_exp,
            'join_other_goods': join_other_goods,
            'other_goods_is_halal': other_goods_is_halal,
            'mix_with_other_goods': mix_with_other_goods,
        }
        show = None
        apply = kw.get('apply') or False
        if not no_lot:
            show = 'no_lot'
        if not show:
            if not waktu_berangkat:
                show = 'waktu_berangkat'
        if not show:
            if not waktu_sampai:
                show = 'waktu_sampai'
        if not show:
            if not has_certificate:
                show = 'has_certificate'
            elif has_certificate == 'yes':
                show = 'certificate_no'
            else:
                if not join_other_goods:
                    show = 'join_other_goods'
                elif join_other_goods == 'no':
                    apply = True
        if not show:
            if not other_goods_is_halal:
                show = 'other_goods_is_halal'
            elif other_goods_is_halal == 'yes':
                apply = True
            elif not mix_with_other_goods:
                show = 'mix_with_other_goods'
            else:
                apply = True

        if apply:
            TransportQuestionnaire = request.env['transport.questionnaire'].sudo()
            vals = {
                'partner_id': request.env.user.partner_id.id,
                'no_lot': no_lot,
                'waktu_berangkat': waktu_berangkat,
                'waktu_sampai': waktu_sampai,
                'has_certificate': has_certificate,
                'certificate_no': certificate_no,
                'certificate_exp': certificate_exp,
                'join_other_goods': join_other_goods,
                'other_goods_is_halal': other_goods_is_halal,
                'mix_with_other_goods': mix_with_other_goods,
            }
            rec = TransportQuestionnaire.create(vals)
            return request.render("transport_questionnaire.portal_new_transport_questionnaire_success", {'rec': rec})
        return request.render("transport_questionnaire.portal_new_transport_questionnaire", 
            {'data': input_data, 'show': show})
