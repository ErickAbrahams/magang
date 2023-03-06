# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers import portal

class CustomerPortal(portal.CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super()._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        values['is_restaurant'] = partner.is_restaurant
        return values

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id

        RestaurantQuestionnaire = request.env['restaurant.questionnaire']
        if 'restaurant_questionnaire_state' in counters:
            questionnaire = RestaurantQuestionnaire.search(self._prepare_questionnaire_domain(partner), limit=1) \
                if RestaurantQuestionnaire.check_access_rights('read', raise_exception=False) else False
            questionnaire_state = questionnaire.state or False
            if questionnaire_state == 'draft':
                questionnaire_state = 'Dalam Proses'
            elif questionnaire_state == 'process':
                questionnaire_state = 'Dalam Proses'
            elif questionnaire_state == 'done':
                questionnaire_state = 'Selesai'
            else:
                questionnaire_state = 'Ajukan'
            values['restaurant_questionnaire_state'] = questionnaire_state

        return values

    def _prepare_questionnaire_domain(self, partner):
        return [
            ('partner_id', 'in', [partner.id]),
            ('state', 'in', ['draft', 'process', 'done'])
        ]

    @http.route(['/my/restaurant_questionnaire', '/my/restaurant_questionnaire/<int:quest_id>'], type='http', auth="user", website=True)
    def portal_restaurant_questionnaire(self, quest_id=None, date_begin=None, date_end=None, sortby=None, **kw):
        RestaurantQuestionnaire = request.env['restaurant.questionnaire']
        partner = request.env.user.partner_id

        if quest_id:
            questionnaire = RestaurantQuestionnaire.browse(quest_id)
            return request.render("restaurant_questionnaire.portal_view_restaurant_questionnaire", {
                    'questionnaire': questionnaire
                })
        else:
            questionnaire = RestaurantQuestionnaire.search(self._prepare_questionnaire_domain(partner), limit=1, order='write_date desc') \
                    if RestaurantQuestionnaire.check_access_rights('read', raise_exception=False) else False
            return request.render("restaurant_questionnaire.portal_my_restaurant_questionnaire", {
                    'questionnaire': questionnaire
                })

    @http.route(['/my/new_restaurant_questionnaire'], type='http', auth="user", website=True)
    def portal_new_restaurant_questionnaire(self, **kw):
        no_lot = kw.get('no_lot') or None
        waktu_kedatangan = kw.get('waktu_kedatangan') or None
        waktu_diolah = kw.get('waktu_diolah') or None
        has_certificate = kw.get('has_certificate') or None
        certificate_no = kw.get('certificate_no') or None
        certificate_exp = kw.get('certificate_exp') or None
        serve_with_gold = kw.get('serve_with_gold') or None
        cook_with_other_goods = kw.get('cook_with_other_goods') or None
        other_goods_is_halal = kw.get('other_goods_is_halal') or None
        input_data = {
            'no_lot': no_lot,
            'waktu_kedatangan': waktu_kedatangan,
            'waktu_diolah': waktu_diolah,
            'has_certificate': has_certificate,
            'certificate_no': certificate_no,
            'certificate_exp': certificate_exp,
            'serve_with_gold': serve_with_gold,
            'cook_with_other_goods': cook_with_other_goods,
            'other_goods_is_halal': other_goods_is_halal
        }
        show = None
        apply = kw.get('apply') or False
        if not no_lot:
            show = 'no_lot'
        if not show:
            if not waktu_kedatangan:
                show = 'waktu_kedatangan'
        if not show:
            if not waktu_diolah:
                show = 'waktu_diolah'
        if not show:
            if not has_certificate:
                show = 'has_certificate'
            elif has_certificate == 'yes':
                show = 'certificate_no'
            else:
                if not serve_with_gold:
                    show = 'serve_with_gold'
                elif serve_with_gold == 'yes':
                    apply = True
        if not show:
            if not cook_with_other_goods:
                show = 'cook_with_other_goods'
            elif cook_with_other_goods == 'no':
                apply = True
            elif not other_goods_is_halal:
                show = 'other_goods_is_halal'
            else:
                apply = True

        if apply:
            RestaurantQuestionnaire = request.env['restaurant.questionnaire'].sudo()
            vals = {
                'partner_id': request.env.user.partner_id.id,
                'no_lot': no_lot,
                'waktu_kedatangan': waktu_kedatangan,
                'waktu_diolah': waktu_diolah,
                'has_certificate': has_certificate,
                'certificate_no': certificate_no,
                'certificate_exp': certificate_exp,
                'serve_with_gold': serve_with_gold,
                'cook_with_other_goods': cook_with_other_goods,
                'other_goods_is_halal': other_goods_is_halal
            }
            rec = RestaurantQuestionnaire.create(vals)
            return request.render("restaurant_questionnaire.portal_new_restaurant_questionnaire_success", {'rec': rec})
        return request.render("restaurant_questionnaire.portal_new_restaurant_questionnaire", 
            {'data': input_data, 'show': show})