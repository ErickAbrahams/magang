odoo.define('expert_system_cf.ExpertSystemForm', function (require) {
    "use static";
    
    var core = require('web.core');
    var ajax = require('web.ajax');

    var publicWidget = require('web.public.widget');
    publicWidget.registry.expertSystemForm = publicWidget.Widget.extend({
        selector: '.o_expert_system_form',
        events: {
            'click .btn-options': '_onClickOptions',
        },
        start: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                self.data = self.$target.data();
                self.options = self.data["options"];
                self.questions = self.data["questions"];
                self.answers = [];
                self._initQuestion();

            });
        },
        _initQuestion: function () {
            this._updateQuestion(0);
        },
        _updateQuestion: function (indexQuestion) {
            var self = this;
            self.indexQuestion = indexQuestion;
            var question = '<p class="text-center">'+self.questions[indexQuestion].question+'</p>';
            var options = '<div class="row text-center my-2 mx-4 d-block"><div class="">';
            self.options.forEach(element => {
                var option = '<button class="btn btn-primary btn-options mx-2 my-1 col-md-2" data-id='+element.id+'>'+element.name+'</button>';
                options += option;
            });
            options += '</div>';
            self.$target.html(question + options);
        },
        _onClickOptions: function (event) {
            event.preventDefault();
            var $target = $(event.currentTarget);
            var id = $target.data()['id'];
        
            var self = this;
            var question = self.questions[self.indexQuestion];
            var answer = {
                'option_id': id,
                'question_id': question.id,
            };
            self.answers.push(answer);
            var newIndex = self.indexQuestion + 1;
            if(newIndex < self.questions.length){
                self._updateQuestion(self.indexQuestion + 1);
            }else{
                this._submitForm(self.answers);
            }
        },
        _submitForm: function (answers) {
            var self = this;
            console.log(JSON.stringify(answers));
            self.$target.html('<p>Mohon menunggu..</p>');
            this._rpc({
                route: '/konsultasi/submit',
                params: {
                    'id': self.data['id'],
                    'answers': answers,
                },
            })
            .then(function (result_form_id) {
                window.location.href = '/konsultasi/form/'+result_form_id;
            });
        
        },
    });
    return publicWidget.registry.expertSystemForm;
});
    