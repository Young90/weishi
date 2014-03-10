function auto_onclick(t) {
    var container = $('.new-edit');
    var type = $('.type');
    var result = $('.result');
    if (t == 'text') {
        ModalManager.show_input_modal('输入要回复的文本', 'textarea', function (input) {
            container.attr('data-type', 'text');
            container.attr('data-value', input);
            type.html('文本回复');
            result.html(input);
        });
        return
    }
    if (t == 'single') {
        ModalManager.show_input_modal('输入单条图文消息的id', 'input', function (input) {
            container.attr('data-type', 'single');
            container.attr('data-value', input);
            type.html('单条图文回复');
            result.html('<a href="/image_article/' + input + '/preview" target="_blank">预览</a>');
        });
        return
    }
    if (t == 'multi') {
        ModalManager.show_input_modal('输入多条图文消息的id', 'input', function (input) {
            container.attr('data-type', 'multi');
            container.attr('data-value', input);
            type.html('多条图文回复');
            result.html('<a href="/image_article_group/' + input + '/preview" target="_blank">预览</a>');
        });
        return
    }
}

$('#auto-save-btn').on('click', function (e) {
    var button = $('#auto-save-btn');
    button.attr('disabled', 'disabled');
    var type = $('.new-edit').attr('data-type');
    var value = $('.new-edit').attr('data-value');
    var aid = $('input[name="aid"]').val();
    if (type == '' || value == '') {
        button.removeAttr('disabled');
        ModalManager.show_failure_modal('请输入内容！');
        return
    }
    var data = {
        type: type,
        value: value
    }
    $.ajax({
        type: 'POST',
        url: '/account/' + aid + '/auto/follow',
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