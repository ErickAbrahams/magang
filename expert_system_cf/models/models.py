
from odoo import models, fields, api


class ExpertSystemCF(models.Model):
    _name = 'expert_system_cf.expert_system_cf'
    _description = 'expert_system_cf.expert_system_cf'

    name = fields.Char(string='Name', required=True)
    question_factor_ids = fields.One2many('expert_system_cf.question', 'expert_system_cf_id', 'Questions')
    option_ids = fields.One2many('expert_system_cf.option', 'expert_system_cf_id', 'Options')


class CFQuestion(models.Model):
    _name = 'expert_system_cf.question'
    _description = 'expert_system_cf.question'
    _rec_name = 'question'

    expert_system_cf_id = fields.Many2one('expert_system_cf.expert_system_cf', 'Expert System CF')
    question = fields.Char(string='Question', required=True)
    cf_1 = fields.Float('CF 1')
    cf_2 = fields.Float('CF 2')

class CFOption(models.Model):
    _name = 'expert_system_cf.option'
    _description = 'expert_system_cf.option'

    expert_system_cf_id = fields.Many2one('expert_system_cf.expert_system_cf', 'Expert System CF')
    name = fields.Char(string='Option', required=True)
    certainty_factor = fields.Float('CF')

class CFForm(models.Model):
    _name = 'expert_system_cf.form'
    _description = 'expert_system_cf.form'

    partner_id = fields.Many2one('res.partner', default=lambda self: self.env.user.partner_id)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
    ], required=True, default='draft', string='Status', copy=False,
        help="The 'Status' is used for evaluating state of form")
    expert_system_cf_id = fields.Many2one('expert_system_cf.expert_system_cf', 'Expert System CF')
    answer_ids = fields.One2many('expert_system_cf.answer', 'form_id', 'Answers')
    result = fields.Char()

    def action_confirm(self):
        for rec in self:
            CF1 = 0
            CF2 = 0
            for answer in rec.answer_ids:
                CF1 = CF1 + answer.question_id.cf_1 * answer.answer.certainty_factor
                CF2 = CF2 + answer.question_id.cf_2 * answer.answer.certainty_factor
            if CF1 > CF2:
                rec.result = 'Daging Sapi.'
            elif CF1 < CF2:
                rec.result = 'Daging Babi.'
            else:
                rec.result = 'Daging Campuran.'
            rec.state = 'done'


    @api.onchange('expert_system_cf_id')
    def onchange_expert_system(self):
        CFAnswer = self.env['expert_system_cf.answer']
        for rec in self:
            answer_ids = []
            for question in rec.expert_system_cf_id.question_factor_ids:
                answer_ids.append((0, 0, {'question_id': question.id, 'form_id': rec.id}))
            rec.answer_ids = answer_ids
    

class CFAnswer(models.Model):
    _name = 'expert_system_cf.answer'
    _description = 'expert_system_cf.answer'

    form_id = fields.Many2one('expert_system_cf.form', 'Form')
    question_id = fields.Many2one('expert_system_cf.question', 'Question')
    answer = fields.Many2one('expert_system_cf.option', 'Answer')

