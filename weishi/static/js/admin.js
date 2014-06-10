function change_user(id) {
    ModalManager.show_input_modal('输入更改后的用户id', 'input', function(input){
        var reg = new RegExp("^[0-9]*$");
        if (!reg.test(input)) {
            ModalManager.show_failure_modal('输入数字');
            return;
        }
        $.ajax({
            type: 'POST',
            url: '/admin/accounts',
            data: {account_id:id,user_id:input},
            success: function(data) {
                if (data.r) {
                    ModalManager.show_success_modal('更改成功！');
                    setTimeout(function(){
                        window.location.reload();
                    }, 1500);
                } else {
                    ModalManager.show_failure_modal(data.error);
                }
            }
        })
    });
}

function save_user() {
    var username = $('input[name=username]').val();
    var email = $('input[name=email]').val();
    var phone = $('input[name=phone]').val();
    var password = $('input[name=password]').val();
    if (username == '' || email == '' || password == '') {
        ModalManager.show_failure_modal('参数不完整！');
        return;
    }
    $.ajax({
            type: 'POST',
            url: '/admin/new_user',
            data: {username:username,email:email,phone:phone,password:password},
            success: function(data) {
                if (data.r) {
                    ModalManager.show_success_modal('添加成功！');
                    setTimeout(function(){
                        window.location = '/admin';
                    }, 1500);
                } else {
                    ModalManager.show_failure_modal(data.error);
                }
            }
        })
}

function change_auth(e, id) {
    var p = $(e).parent();
    var form = $(p).find('input[name=form]').is(':checked') ?1:0;
    var site = $(p).find('input[name=site]').is(':checked') ?1:0;
    var card = $(p).find('input[name=card]').is(':checked') ?1:0;
    var impact = $(p).find('input[name=impact]').is(':checked') ?1:0;
    var menu = $(p).find('input[name=menu]').is(':checked') ?1:0;
    var event = $(p).find('input[name=event]').is(':checked') ?1:0;
    var canyin = $(p).find('input[name=canyin]').is(':checked') ?1:0;
    var ps = {form: form, site:site, card:card, impact:impact, menu:menu, event:event, canyin:canyin, id:id};
    $.ajax({
        url: '/admin/auth',
        type: 'POST',
        data: ps,
        success: function(data) {
            if (data.r) {
                window.location.reload();
            }
        }
    })
};