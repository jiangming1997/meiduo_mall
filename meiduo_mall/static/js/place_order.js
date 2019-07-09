// var vm = new Vue({
//     el: '#app',
// 	// 修改Vue变量的读取语法，避免和django模板语法冲突
//     delimiters: ['[[', ']]'],
//     data: {
//         host: host,
//         order_submitting: false, // 正在提交订单标志
//         pay_method: 2, // 支付方式,默认支付宝支付
//         nowsite: '', // 默认地址
//         payment_amount: '',
//
//     },
//     mounted(){
//         // 初始化
//         this.payment_amount = payment_amount;
//         // 绑定默认地址
//         this.nowsite = default_address_id;
//     },
//     methods: {
//         // 提交订单
//         on_order_submit(){
//             if (!this.nowsite) {
//                 alert('请补充收货地址');
//                 return;
//             }
//             if (!this.pay_method) {
//                 alert('请选择付款方式');
//                 return;
//             }
//             if (this.order_submitting == false){
//                 this.order_submitting = true;
//                 var url = this.host + '/orders/commit/';
//                 axios.post(url, {
//                         address_id: this.nowsite,
//                         pay_method: parseInt(this.pay_method)
//                     }, {
//                         headers:{
//                             'X-CSRFToken':getCookie('csrftoken')
//                         },
//                         responseType: 'json'
//                     })
//                     .then(response => {
//                         if (response.data.code == '0') {
//                             location.href = '/orders/success/?order_id='+response.data.order_id
//                                         +'&payment_amount='+this.payment_amount
//                                         +'&pay_method='+this.pay_method;
//                         } else if (response.data.code == '4101') {
//                             location.href = '/login/?next=/orders/settlement/';
//                         } else {
//                             alert(response.data.errmsg);
//                         }
//                     })
//                     .catch(error => {
//                         this.order_submitting = false;
//                         console.log(error.response);
//                     })
//             }
//         },
//         ins_select(){
//             if (this.value == "0"){
//                  var choice=0
//                 var url = this.host + '/orders/settlement/';
//                 axios.post(url, {
//                         choice
//
//                     }, {
//                         headers:{
//                             'X-CSRFToken':getCookie('csrftoken')
//                         },
//                         responseType: 'json'
//                     })
//                     .catch(error => {
//                         this.order_submitting = false;
//                         console.log(error.response);
//                     })
//             }
//             if (this.value == "1"){
//                  var choice=1
//                 var url = this.host + '/orders/settlement/';
//                 axios.post(url, {
//                         choice
//
//                     }, {
//                         headers:{
//                             'X-CSRFToken':getCookie('csrftoken')
//                         },
//                         responseType: 'json'
//                     })
//                     .catch(error => {
//                         this.order_submitting = false;
//                         console.log(error.response);
//                     })
//             }
//
//         }
//
// }
//
//     },
//
// });

var vm = new Vue({
    el: '#app',
    // 修改Vue变量的读取语法，避免和django模板语法冲突
    delimiters: ['[[', ']]'],
    data: {
        host: host,
        order_submitting: false, // 正在提交订单标志
        pay_method: 2, // 支付方式,默认支付宝支付
        nowsite: '', // 默认地址
        payment_amount: '',
        skus_length: '',
        select_integral: "false",
        new_payment_amount: '',
        new_counpon_amout: '',
    },
    mounted() {
        // 初始化
        this.payment_amount = payment_amount;
        this.new_payment_amount = new_payment_amount;
        this.new_counpon_amout = new_counpon_amout;
        // 绑定默认地址
        this.nowsite = default_address_id;
        //判断是否有商品
        this.skus_length = skus_length;
    },
    methods: {
        // 提交订单
        on_order_submit() {
            if (!this.nowsite) {
                alert('请补充收货地址');
                return;
            }
            if (!this.pay_method) {
                alert('请选择付款方式');
                return;
            }
            if (!this.skus_length) {
                alert('请先添加商品');
                return;
            }
            if (this.order_submitting == false) {
                this.order_submitting = true;
                var url = this.host + '/orders/commit/';
                axios.post(url, {
                    select_integral: this.select_integral,
                    address_id: this.nowsite,
                    pay_method: parseInt(this.pay_method)

                }, {
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    responseType: 'json'
                })
                    .then(response => {
                        if (response.data.code == '0') {
                            if (this.select_integral == "false") {
                                location.href = '/orders/success/?order_id=' + response.data.order_id
                                    + '&payment_amount=' + this.new_payment_amount
                                    + '&pay_method=' + this.pay_method;


                            }
                            else if (this.select_integral == "true") {
                                location.href = '/orders/success/?order_id=' + response.data.order_id
                                    + '&payment_amount=' + this.new_counpon_amout
                                    + '&pay_method=' + this.pay_method;


                            }
                            else {
                                location.href = '/orders/success/?order_id=' + response.data.order_id
                                    + '&payment_amount=' + this.payment_amount
                                    + '&pay_method=' + this.pay_method;
                            }

                        } else if (response.data.code == '4101') {
                            location.href = '/login/?next=/orders/settlement/';
                        } else {
                            alert(response.data.errmsg);
                        }
                    })
                    .catch(error => {
                        this.order_submitting = false;
                        console.log(error.response);
                    })
            }
        }
    }
});
