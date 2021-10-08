odoo.define('osynx_loan.submit_payment', function (require) {
    "use strict";
    
    var core = require('web.core');
    var publicWidget = require('web.public.widget');
    var rpc = require('web.rpc');
    var time = require('web.time');

    var _t = core._t;
    var Dialog = require('web.Dialog');
    
    publicWidget.registry.submit_payment = publicWidget.Widget.extend({
        $("#payment_type").change(function() {

            if ( $(this).val() == "contribution") {

                $("#loan_id").hide();

    //            $("#txtcboState").show();

            }
//            else{
//
//                $("#cboState").show();
//                $("#txtcboState").hide();
//            }

        });

    });
});