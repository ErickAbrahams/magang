var lot_number = `
<p class="text-center">Nomor Lot</p>
<div class="row text-center my-2 mx-4 d-block">
    <input type="text" name="lot_number" placeholder="Nomor Lot" required/>
</div>
`;
var waktu_potong = `
<p class="text-center">Waktu Potong</p>
<div class="row text-center my-2 mx-4 d-block">
    <input type="text" name="waktu_potong" placeholder="Waktu Potong" required/>
</div>
`;
var waktu_kirim = `
<p class="text-center">Waktu Kirim</p>
<div class="row text-center my-2 mx-4 d-block">
    <input type="text" name="waktu_kirim" placeholder="Waktu Kirim" required/>
</div>
`;
var list_questions = [
	{
    "name": "lot_number",
    "html": lot_number
    },
	{
    "name": "waktu_potong",
    "html": waktu_potong
    },
	{
    "name": "waktu_kirim",
    "html": waktu_kirim
    }
];

odoo.define('rph_questionnaire.rph_questionnaire', function (require) {
	"use static";

    var core = require('web.core');
    var ajax = require('web.ajax');

    var publicWidget = require('web.public.widget');
    publicWidget.registry.RPHQuestionnaireForm = publicWidget.Widget.extend({
    	selector: '.rph_questionnaire_container',
        events: {
            'click .btn-next': '_onClickOptions',
        },
        start: function () {
            var self = this;
            console.log("-----------");
            return this._super.apply(this, arguments).then(function () {
                self.questions = list_questions;
                self.answers = [];
                self._updateQuestion(0);
            });
        },
        _updateQuestion: function (indexQuestion) {
            var self = this;
            self.indexQuestion = indexQuestion;
            var q = self.questions[indexQuestion];

            var btnSubmit = `
            <div class="row text-center my-2 mx-4 d-block">
                <input type="submit" class="btn btn-primary btn-next"/>
            </div>
            `;
            
            self.$target.html(q.html + btnSubmit);
        },
        _onClickOptions: function (event) {
            var self = this;
            self._updateQuestion(self.indexQuestion + 1);
            return false;
        },
    });
    return publicWidget.registry.RPHQuestionnaireForm;
});
