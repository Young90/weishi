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