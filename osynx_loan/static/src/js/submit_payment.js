odoo.define('osynx_loan.submit_payment', function (require) {
    "use strict";

    var core = require('web.core');
    var publicWidget = require('web.public.widget');
    var rpc = require('web.rpc');
    var time = require('web.time');

    var _t = core._t;
    var Dialog = require('web.Dialog');

    publicWidget.registry.submit_material = publicWidget.Widget.extend({
        selector: '#wrapwrap:has(.add_requisition_product_form)',
        events: {
            /*'change select.uom_id' : function (e) {
                e.preventDefault();
                var self = this;
                self._onChangeUOM(this.$('select.uom_id').val());
            },*/
            'click .submit_payment_form .action_create_payment': '_onCreateNewPayment',
        },
        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------

        /**
         * @private
         * @param {jQuery} $btn
         * @param {function} callback
         * @returns {Promise}
         */
        _buttonExec: function ($btn, callback) {
            // TODO remove once the automatic system which does this lands in master
            $btn.prop('disabled', true);
            return callback.call(this).guardedCatch(function () {
                $btn.prop('disabled', false);
            });
        },
        /**
         * @private
         * @returns {Promise}
         */

        init: function (parent, options) {
            this._super.apply(this, arguments);
        },
        start: function () {
            var self = this;
            return Promise.all([
                this._super(),
                /*this.$('.uom_id').each(function () {
                    self._onChangeUOM($(this).val());
                }),*/
            ])
        },
        /*_onChangeUOM: function(val){
            var self = this;
            this._rpc({
                model : 'hr.leave.type',
                method: 'search_read',
                args: [[['id', '=', val]], ['id', 'request_unit']],
            }).then(function(rec){
                if (rec && rec[0]){
                    if (rec[0].request_unit == 'hour'){
                        $('.request_unit_half_div').show();
                        $('.request_unit_hours_div').show();
                    }
                    else if (rec[0].request_unit == 'half_day'){
                        $('.request_unit_half_div').show();
                        $('.request_unit_hours_div').hide();
                    }
                    else{
                        $('.request_unit_half_div').hide();
                        $('.request_unit_hours_div').hide();
                        $('.request_date_from_div').show();
                    }
                }
            });
        },*/
        _onCreateNewPayment: function(ev){
            ev.preventDefault();
            ev.stopPropagation();
            var quantity = $('.submit_payment_form .product_type').val();

            if (!product_type) {
                this.do_notify(false, _t("Please Enter Product Type"));
                return;
            }
            this._buttonExec($(ev.currentTarget), this._createNewPayment);
        },
        _createNewPayment: function(){
            return this._rpc({
                model: 'loan.purchase.requisition',
                method: 'create_payment',
                args: [{
                    product_type: $('.submit_payment_form .product_type').val(),
                }],
            })
            .then(function (response) {
                if (response.errors) {
                    $('#new-product-dialog .alert').remove();
                    $('#new-product-dialog div:first').prepend('<div class="alert alert-danger">' + response.errors + '</div>');
                    return Promise.reject(response);
                } else {
                    /*window.location = '/material/request/product/form/' + response.id + '?access_token=' + response.access_token;*/
                    window.location = '/material/request/form/' + response.id;
                }
            });
        },
    });
});

/*
odoo.define('osynx_loan.submit_payment', function (require) {
    "use strict";

        var core = require('web.core');
        var publicWidget = require('web.public.widget');
        var rpc = require('web.rpc');
        var time = require('web.time');

        var _t = core._t;
         var Dialog = require('web.Dialog');

        $("#loan_id_label").hide();
        $("#loan_id").hide();
        $("#member_id").prop("selectedIndex", -1);

        //  ONCHANGE PAYMENT TYPE
        $("#payment_type").change(function()
        {
             if($(this).val() == "interest" || $(this).val() == "principal")
                {
                    $("#loan_id_label").show();
                    $("#loan_id").show();
                }
            else
                {
                    $("#loan_id_label").hide();
                    $("#loan_id").hide();
                }
        });
        // END

        publicWidget.registry.submit_material = publicWidget.Widget.extend({
        selector: '#wrapwrap:has(.submit_payment_form)',
        events: {
            */
/*'change select.uom_id' : function (e) {
                e.preventDefault();
                var self = this;
                self._onChangeUOM(this.$('select.uom_id').val());
            },*//*


            'click .submit_payment_form .action_create_payment': '_onCreatePayment',
        },
        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------

        */
/**
         * @private
         * @param {jQuery} $btn
         * @param {function} callback
         * @returns {Promise}
         *//*

        _buttonExec: function ($btn, callback) {
            // TODO remove once the automatic system which does this lands in master
            $btn.prop('disabled', true);
            return callback.call(this).guardedCatch(function () {
                $btn.prop('disabled', false);
            });
        },
        */
/**
         * @private
         * @returns {Promise}
         *//*


        init: function (parent, options) {
            this._super.apply(this, arguments);
        },
        start: function () {
            var self = this;
            return Promise.all([
                this._super(),
            ])
        },
        _onCreatePayment: function(ev){
            ev.preventDefault();
            ev.stopPropagation();
            var payment_type = $('.submit_payment_form .payment_type').val();

            Dialog.confirm(self, _t("This will create payment. Do you still want to proceed ?"), {
                confirm_callback: function() {
                    self._onDeleteRequest(material_requisition_id);
                },
                title: _t('Create payment'),
            });

            if (!payment_type) {
                this.do_notify(false, _t("Please Enter Payment Type"));
                return;
            }
            this._buttonExec($(ev.currentTarget), this._createPayment);
        },
        _createPayment: function(){
            return this._rpc({
                model: 'account.loan.payment',
                method: 'create_payment',
                args: [{
                    payment_type: $('.submit_payment_form .payment_type').val();
                    loan_id: $('.submit_payment_form .loan_id').val();
                    date: $('.submit_payment_form .date').val();
                    amount: $('.submit_payment_form .amount').val();
                    attachment: $('.submit_payment_form .attachment').val();
                }],
            })
            .then(function (response) {
                if (response.errors) {
                    $('#new-product-dialog .alert').remove();
                    $('#new-product-dialog div:first').prepend('<div class="alert alert-danger">' + response.errors + '</div>');
                    return Promise.reject(response);
                } else {
                    */
/*window.location = '/material/request/product/form/' + response.id + '?access_token=' + response.access_token;*//*

                    window.location = '/material/request/form/' + response.id;
                }
            });
        },
    });
});*/
