/*accounts js in weishi project by shenguan*/

// bind submit handler to #addAccountForm
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
    if (app_id == '' || app_secret == '') {
        button.removeAttr('disabled');
        ModalManager.show_failure_modal('信息没有填入！');
        return
    }
    var data = {
        'app_id': app_id,
        'app_secret': app_secret
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