function submit_reg_form(n, m, a) {
    var button = $('#card-save-btn');
    button.attr('disabled', 'disabled');
    var name = '';
    if (n == 1) {
        name = $('input[name="name"]').val();
        if (name == '') {
            button.removeAttr('disabled');
            ModalManager.show_failure_modal('还没填写姓名呢！');
            return
        }
    }
    var mobile = '';
    if (m == 1) {
        mobile = $('input[name="mobile"]').val();
        if (mobile == '') {
            button.removeAttr('disabled');
            ModalManager.show_failure_modal('还没填写手机号呢！');
            return
        }
        if (!(/^0?(13[0-9]|15[012356789]|18[0236789]|14[57])[0-9]{8}$/.test(mobile))) {
            button.removeAttr('disabled');
            ModalManager.show_failure_modal('输入的手机号码格式不正确！');
            return
        }
    }
    var address = '';
    if (a == 1) {
        address = $('input[name="address"]').val();
        if (address == '') {
            button.removeAttr('disabled');
            ModalManager.show_failure_modal('还没填写地址呢！');
            return
        }
    }
    var cid = $('input[name="cid"]').val();
    var openid = $('input[name="openid"]').val();
    var data = {
        'name': name,
        'mobile': mobile,
        'address': address,
        'openid': openid
    }
    $.ajax({
        type: 'POST',
        url: '/card/' + cid,
        data: data,
        success: function(data) {
            if (data.r) {
                ModalManager.show_success_modal('保存成功！');
                setTimeout(function () {
                    window.location.reload();
                }, 1500);
            } else {
                button.removeAttr('disabled');
                ModalManager.show_failure_modal(data.error);
            }
        }
    })
};