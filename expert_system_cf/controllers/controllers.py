# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class ExpertSystemCf(http.Controller):
    @http.route('/konsultasi', type='http', auth="user", website=True)
    def index(self, **kw):
        ExpertSystemCF = request.env['expert_system_cf.expert_system_cf'].sudo()
        expert_system = ExpertSystemCF.search([], limit=1)
        if expert_system:
            questions = []
            for question in expert_system.question_factor_ids:
                questions.append({
                    'id': question.id,
                    'question': question.question,
                })
            options = []
            for option in expert_system.option_ids:
                options.append({
                    'id': option.id,
                    'name': option.name,
                })
            return request.render("expert_system_cf.portal_expert_system_form", {
                'questions': questions,
                'options': options,
                'name': expert_system.name,
                'id': expert_system.id
            })
        return request.not_found(description='Feature you are looking is not ready yet. Please check again or ask administrator.')

    @http.route('/konsultasi/submit', type='json', auth="user", website=True)
    def submit(self, **kw):
        ExpertSystemForm = request.env['expert_system_cf.form'].sudo()
        ExpertSystemAnswer = request.env['expert_system_cf.answer'].sudo()
        answers = []
        for answer in kw.get('answers'):
            answer_id = ExpertSystemAnswer.create({
                'question_id': answer.get('question_id'),
                'answer': answer.get('option_id')
            })
            answers.append(answer_id.id)
        res = ExpertSystemForm.create({
            'expert_system_cf_id': kw.get('id'),
            'answer_ids': answers
        })
        res.action_confirm()
        return res.id

    @http.route('/konsultasi/form/<int:form_id>', type='http', auth="user", website=True)
    def form(self, form_id, **kw):
        ExpertSystemForm = request.env['expert_system_cf.form'].sudo()
        print('form_id = %d' % (form_id))
        form = ExpertSystemForm.browse(form_id)
        print('form = ')
        print(form)
        if form:
            return request.render("expert_system_cf.portal_expert_system_form_result", {
                'form': form,
            })
        else:
            return request.not_found(description='Form you are looking could not be found. Please check again or ask administrator.')
