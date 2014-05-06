$('#addAccountForm').on('submit', function (e) {
    e.preventDefault(); // prevent native submit
    var submitBtn = $('#addAccountBtn'),
        btnText = '添加';
    $(this).ajaxSubmit({
        dataType: 'json',
        beforeSubmit: function () {
            if (checkInputsEmpty()) {
                return false;
            }
            changeBtnStatus(submitBtn, 'loading');
        },
        success: function (data) {
            if (data.r == 1) {
                window.location = '/account/' + data.aid;
            } else {
                $('.alert-danger').text(data.error).fadeIn();
                changeBtnStatus(submitBtn, 'normal', btnText);
            }
        },
        error: function () {
            $('.alert-danger').text('网络出错，添加失败，请重试！').fadeIn();
            changeBtnStatus(submitBtn, 'normal', btnText);
        }
    })
});

var changeBtnStatus = function (btn, status, text) {
    if (status == 'loading') {
        var btnLoading = '<span class="loading"></span>';
        btn.attr('disabled', 'disabled').html(btnLoading);
    } else if (status == 'normal') {
        btn.removeAttr('disabled').html(text);
    } else if (status == 'disabled') {
        btn.attr('disabled', 'disabled').html(text);
    }
}

function checkInputsEmpty() {
    var hasEmpty = false;
    $('.form-control').each(function () {
        var _target = $(this);
        if (_target.val() == '') {
            _target.parent().addClass('has-error');
            hasEmpty = true;
        } else {
            _target.parent().removeClass('has-error');
        }
    });
    $('.alert-danger').fadeOut();
    return hasEmpty;
}

$('#app-save-btn').on('click', function () {
    var button = $('#app-save-btn');
    button.attr('disabled', 'disabled');
    var app_id = $('input[name="app_id"]').val();
    var app_secret = $('input[name="app_secret"]').val();
    var wei_account = $('input[name="wei_account"]').val();
    if (app_id == '' || app_secret == '' || wei_account == '') {
        button.removeAttr('disabled');
        ModalManager.show_failure_modal('信息没有填入！');
        return
    }
    var data = {
        'app_id': app_id,
        'app_secret': app_secret,
        'wei_account': wei_account
    }
    $.ajax({
        type: 'POST',
        url: '/accounts/update',
        data: data,
        success: function (data) {
            button.removeAttr('disabled');
            if (data.r) {
                ModalManager.show_success_modal('保存成功！');
                setTimeout(function () {
                    window.location.reload();
                }, 1500);
            } else {
                ModalManager.show_failure_modal(data.error);
            }
        }
    })
});

$('#card-save-btn').on('click', function () {
    var button = $('#card-save-btn');
    button.attr('disabled', 'disabled');
    var link = window.location.href;
    var register = $('input[name="register"]').is(':checked') ? 1 : 0;
    var name = $('input[name="name"]').is(':checked') ? 1 : 0;
    var mobile = $('input[name="mobile"]').is(':checked') ? 1 : 0;
    var address = $('input[name="address"]').is(':checked') ? 1 : 0;
    var phone = $('input[name="phone"]').val();
    var about = $('textarea[name="about"]').val();
    var thumb = $('.thumb>a').attr('href');
    var cover = $('.cover>a').attr('href');
    var data = {
        'register': register,
        'name': name,
        'thumb': thumb,
        'cover': cover,
        'mobile': mobile,
        'address': address,
        'phone': phone,
        'about': about
    }
    $.ajax({
        type: 'POST',
        url: link,
        data: data,
        success: function (data) {
            button.removeAttr('disabled');
            if (data.r) {
                ModalManager.show_success_modal('保存成功！');
                setTimeout(function () {
                    window.location.reload();
                }, 1500);
            }
        }
    })
});

$('#impacts-save-btn').on('click', function () {
    var button = $('#impacts-save-btn');
    button.attr('disabled', 'disabled');
    var link = window.location.href;
    var c_list = $('.card-create');
    var param = [];
    for (var i = 0; i < c_list.length; i++) {
        var name = $(c_list[i]).find('input[name="name"]').val();
        var num = $(c_list[i]).find('input[name="num"]').val();
        var p = {
            'name': name,
            'num': num
        }
        param.push(p);
    }
    var data = {
        'params': JSON.stringify(param)
    }
    $.ajax({
        type: 'POST',
        url: link,
        data: data,
        success: function (data) {
            button.removeAttr('disabled');
            if (data.r) {
                ModalManager.show_success_modal('保存成功！');
                setTimeout(function () {
                    window.location.reload();
                }, 1500);
            }
        }
    })
});