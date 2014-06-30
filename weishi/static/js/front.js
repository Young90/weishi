function submit_reg_form(n, m, a, s, b) {
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
        if (!(/^0?(13[0-9]|15[0-9]|18[0-9]|14[0-9]|17[0-9])[0-9]{8}$/.test(mobile))) {
            button.removeAttr('disabled');
            ModalManager.show_failure_modal('输入正确的手机号，不能包含空格横线等字符！');
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
    var sex = '';
    if (s == 1) {
        sex = $('input[name="sex"]:checked').val();
        if (sex == '') {
            button.removeAttr('disabled');
            ModalManager.show_failure_modal('还没选择性别呢！');
            return
        }
    }
    var birthday = '';
    if (b == 1) {
        birthday = $('input[name="birthday"]').val();
        if (birthday == '') {
            button.removeAttr('disabled');
            ModalManager.show_failure_modal('还没填写生日呢！');
            return
        }
    }
    var cid = $('input[name="cid"]').val();
    var openid = $('input[name="openid"]').val();
    var data = {
        'name': name,
        'mobile': mobile,
        'address': address,
        'birthday': birthday,
        'sex': sex,
        'openid': openid
    }
    $.ajax({
        type: 'POST',
        url: '/card/' + cid,
        data: data,
        success: function (data) {
            if (data.r) {
                ModalManager.show_success_modal('注册成功！');
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

function add_impact(id, name) {
    var link = window.location.href;
    var aid = $('input[name="aid"]').val();
    var data = {
        'id': id
    }
    $.ajax({
        type: 'POST',
        data: data,
        url: link,
        success: function (data) {
            if (data.r) {
                document.cookie = 'i_' + aid + '=' + escape(name);
                ModalManager.show_success_modal('添加成功！');
                setTimeout(function () {
                    window.location.reload();
                }, 1500);
            } else {
                ModalManager.show_failure_modal(data.error);
            }
        }
    })
}

function add_impact_local() {
    ModalManager.show_input_modal('输入你的印象', 'input', function (input) {
        var aid = $('input[name="aid"]').val();
        document.cookie = 'i_' + aid + '=' + escape(input);
        ModalManager.show_success_modal('添加成功！');
        setTimeout(function () {
            window.location.reload();
        }, 1500);
    });
}