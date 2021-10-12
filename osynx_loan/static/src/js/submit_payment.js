odoo.define('osynx_loan.submit_payment', function (require) {
    "use strict";

         var rpc = require('web.rpc');

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

       /* var Widget = require('web.Widget');
        var Counter = require('myModule.Counter');

        var MyWidget = Widget.extend({
            custom_events: {
                valuechange: 'changeMember'
            },
            start: function () {
                this.counter = new Counter(this);
                var def = this.counter.appendTo(this.$el);
                return Promise.all([def, this._super.apply(this, arguments)]);
            },

            changeMember(event){
            this.change[event.target.name] = event.target.value;
            var self = this;

            var member_id =  self.changes['member_id']

            rpc_result = rpc.query({
				model: 'loan.account',
				method: 'get_loan_account_domain',
				args: [member_id],

			}).then(function(output) {
				my_user = partner_id['id']
				total_amt = parseFloat(partner_id.wallet_balance) + parseFloat(entered_amount)
				partner_id.wallet_balance = total_amt
				$('.client-detail').find('#wallet_bal').html(total_amt);
				$('.client-list .highlight').find('#bal').html(total_amt);
				alert('Wallet is Successfully Recharge !!!!');
				self.trigger('close-temp-screen');
				self.trigger('close-popup');
				self.showTempScreen('ClientListScreen');

			});
		}
        });*/


        }
//        $('#loan_id').append($('<option>',{text: 'pippo', value: 'pippo', selected: true}))

});