odoo.define('osyn_loan.form', function (require) {
'use strict';

var core = require('web.core');
var FormEditorRegistry = require('website_form.form_editor_registry');

var _t = core._t;

FormEditorRegistry.add('submit_contribution', {
    formFields: [
    {
        type: 'many2one',
        name: 'name',
        string: 'Name',
    }, {

        type: 'float',
        name: 'amount',
        string: 'Amount',
    }, {
        type: 'date',
        name: 'date',
        string: 'Date',
    }
    ],
    successPage: '/job-thank-you',
});

});
