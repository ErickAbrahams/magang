# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers import portal

class CustomerPortal(portal.CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super()._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        values['is_storage'] = partner.is_storage
        return values

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id

        StorageQuestionnaire = request.env['storage.questionnaire']
        if 'storage_questionnaire_state' in counters:
            questionnaire = StorageQuestionnaire.search(self._prepare_questionnaire_domain(partner), limit=1) \
                if StorageQuestionnaire.check_access_rights('read', raise_exception=False) else False
            
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
            values['storage_questionnaire_state'] = questionnaire_state

        return values

    def _prepare_questionnaire_domain(self, partner):
        return [
            ('partner_id', '=', [partner.id]),
            ('state', 'in', ['draft', 'process', 'done'])
        ]

    @http.route(['/my/storage_questionnaire', '/my/storage_questionnaire/<int:quest_id>'], type='http', auth="user", website=True)
    def portal_storage_questionnaire(self, quest_id=None, date_begin=None, date_end=None, sortby=None, **kw):
        StorageQuestionnaire = request.env['storage.questionnaire']
        partner = request.env.user.partner_id

        if quest_id:
            questionnaire = StorageQuestionnaire.browse(quest_id)
            return request.render("storage_questionnaire.portal_view_storage_questionnaire", {
                    'questionnaire': questionnaire
                })
        else:
            questionnaire = StorageQuestionnaire.search(self._prepare_questionnaire_domain(partner), limit=1, order='write_date desc') \
                    if StorageQuestionnaire.check_access_rights('read', raise_exception=False) else False
            return request.render("storage_questionnaire.portal_my_storage_questionnaire", {
                    'questionnaire': questionnaire
                })
    
    @http.route(['/my/new_storage_questionnaire'], type='http', auth="user", website=True)
    def portal_new_storage_questionnaire(self, **kw):
        no_lot = kw.get('no_lot') or None
        waktu_disimpan = kw.get('waktu_disimpan') or None
        waktu_keluar = kw.get('waktu_keluar') or None
        has_certificate = kw.get('has_certificate') or None
        certificate_no = kw.get('certificate_no') or None
        certificate_exp = kw.get('certificate_exp') or None
        join_other_goods = kw.get('join_other_goods') or None
        other_goods_is_halal = kw.get('other_goods_is_halal') or None
        mix_with_other_goods = kw.get('mix_with_other_goods') or None
        input_data = {
            'no_lot': no_lot,
            'waktu_disimpan': waktu_disimpan,
            'waktu_keluar': waktu_keluar,
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
            if not waktu_disimpan:
                show = 'waktu_disimpan'
        if not show:
            if not waktu_keluar:
                show = 'waktu_keluar'
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
            StorageQuestionnaire = request.env['storage.questionnaire'].sudo()
            vals = {
                'partner_id': request.env.user.partner_id.id,
                'no_lot': no_lot,
                'waktu_disimpan': waktu_disimpan,
                'waktu_keluar': waktu_keluar,
                'has_certificate': has_certificate,
                'certificate_no': certificate_no,
                'certificate_exp': certificate_exp,
                'join_other_goods': join_other_goods,
                'other_goods_is_halal': other_goods_is_halal,
                'mix_with_other_goods': mix_with_other_goods,
            }
            rec = StorageQuestionnaire.create(vals)
            return request.render("storage_questionnaire.portal_new_storage_questionnaire_success", {'rec': rec})
        return request.render("storage_questionnaire.portal_new_storage_questionnaire", 
            {'data': input_data, 'show': show})
