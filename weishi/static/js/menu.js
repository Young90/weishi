/**
 * Created by young on 14-2-21.
 */

function add_main_menu() {
    var items = $('.edit-menu');
    if (items.length >= 3) {
        ModalManager.show_failure_modal('一级菜单最多只能有三个！');
        return;
    }
    var main_menu_html = '<div class="edit-menu">' +
        '<div class="menu-item">' +
        '<div class="main-container" data-type="" data-value="">' +
        '<div class="input-container">' +
        '<input type="text" name="main" class="form-control input-lg main" placeholder="一级菜单名称">' +
        '<span class="result"></span>' +
        '</div>' +
        '<div class="op">' +
        ' <span class="action black">回复内容 </span>' +
        '<span class="action"><a href="javascript:;" onclick="javascript:show_input_text_dialog(this);">文本</a></span>' +
        '<span class="action"><a href="javascript:;" onclick="javascript:show_input_single_dialog(this);">单条图文</a></span>' +
        '<span class="action"><a href="javascript:;" onclick="javascript:show_input_multi_dialog(this);">多条图文</a></span>' +
        '<span class="action"><a href="javascript:;" onclick="javascript:show_input_link_dialog(this);">链接</a></span>' +
        '<span class="action"><a href="javascript:;" onclick="javascript:add_some_with_name(this, "会员卡", "card");">会员卡</a></span>' +
        '<span class="action remove"><a href="javascript:;" onclick="javascript:remove_main_menu(this);">删除</a></span>' +
        '</div>' +
        '</div>' +
        '</div>' +
        '<div class="add-sub-click">' +
        '<a href="javascript:;" onclick="javascript:add_sub_menu(this);">+添加二级菜单</a>' +
        '</div>' +
        '</div>';
    var parent = $('.menu-edit');
    parent.append(main_menu_html);
};

function add_sub_menu(obj) {
    var container = $(obj).parent().parent();
    $(container).find('.main-container').find('.result').html('');
    $(container).find('.main-container').attr('data-type', 'button');
    $(container).find('.main-container').attr('data-value', '');
    $(container).find('.main-container').find('.op').css('display', 'None');
    var items = $(container).find('.sub-container');
    if (items.length >= 5) {
        ModalManager.show_failure_modal('二级菜单最多五个！');
        return;
    }
    var sub_html = '<div class="sub-container" data-type="" data-value="">' +
        '<div class="input-container">' +
        '<input type="text" name="sub" class="form-control input-lg main" placeholder="二级菜单名称">' +
        '<span class="result"></span>' +
        '</div>' +
        '<div class="op">' +
        '<span class="action black">回复内容 </span>' +
        '<span class="action"><a href="javascript:;" onclick="javascript:show_input_text_dialog(this);">文本</a></span>' +
        '<span class="action"><a href="javascript:;" onclick="javascript:show_input_single_dialog(this);">单条图文</a></span>' +
        '<span class="action"><a href="javascript:;" onclick="javascript:show_input_multi_dialog(this);">多条图文</a></span>' +
        '<span class="action"><a href="javascript:;" onclick="javascript:show_input_link_dialog(this);">链接</a></span>' +
        '<span class="action"><a href="javascript:;" onclick="javascript:add_some_with_name(this, "会员卡", "card");">会员卡</a></span>' +
        '<span class="action remove"><a href="javascript:;" onclick="javascript:remove_sub_menu(this);">删除</a></span>' +
        '</div>' +
        '</div>';
    var main = $(container).find('.menu-item');
    $(main).append(sub_html);
}

function remove_sub_menu(obj) {
    var sub_container = $(obj).parents('.sub-container');
    ModalManager.show_confirm_modal('确定移除此二级菜单吗？', function (result) {
        var container = $(sub_container).parents('.menu-item');
        if ($(container).find('.sub-container').length == 1) {
            $(container).find('.op').css('display', 'block');
            $(container).find('.main-container').attr('data-type', '');
        }
        if (result) {
            $(sub_container).remove();
        }
    });
}

function remove_main_menu(obj) {
    var container = $(obj).parents('.edit-menu');
    ModalManager.show_confirm_modal('所有的二级菜单也将移除，确定吗？', function (result) {
        if (result) $(container).remove();
    });
}

function show_input_text_dialog(obj) {
    ModalManager.show_input_modal('输入要回复的文本信息', 'textarea', function (input) {
        var container = $(obj).parents('.op').parent();
        var result = $(container).find('.result');
        $(container).attr('data-type', 'text');
        $(container).attr('data-value', input);
        $(result).html('文本：' + input);
    });
}

function show_input_single_dialog(obj) {
    ModalManager.show_input_modal('输入单条图文的id', 'input', function (input) {
        var container = $(obj).parents('.op').parent();
        var result = $(container).find('.result');
        $(container).attr('data-type', 'single');
        $(container).attr('data-value', input);
        $(result).html('单条图文：' + '<a target="_blank" href="/image_article/' + input + '/preview">预览</a>');
    });
};

function show_input_multi_dialog(obj) {
    ModalManager.show_input_modal('输入多条图文的id', 'input', function (input) {
        var container = $(obj).parents('.op').parent();
        var result = $(container).find('.result');
        $(container).attr('data-type', 'multi');
        $(container).attr('data-value', input);
        $(result).html('多条图文：' + '<a target="_blank" href="/image_article_group/' + input + '/preview">预览</a>');
    });
};

function show_input_link_dialog(obj) {
    ModalManager.show_input_modal('输入链接地址', 'input', function (input) {
        var container = $(obj).parents('.op').parent();
        var result = $(container).find('.result');
        $(container).attr('data-type', 'link');
        $(container).attr('data-value', input);
        $(result).html('链接地址：' + '<a target="_blank" href="' + input + '">查看</a>');
    });
};

function add_some_with_name(obj, name, value) {
    var container = $(obj).parents('.op').parent();
        var result = $(container).find('.result');
        $(container).attr('data-type', value);
        $(container).attr('data-value', value);
        $(result).html(name);
};

$('#menu-save-btn').on('click', function () {
    ModalManager.show_process_modal();
    var button = $('#menu-save-btn');
    button.attr('disabled', 'disabled');
    var items = $('.edit-menu');
    var result = [];
    var aid = $('input[name="aid"]').val();
    for (var i = 0; i < items.length; i++) {
        var item = items[i];
        var main_container = $(item).find('.main-container');
        var main_name = $(main_container).find('input[name="main"]').val();
        if (main_name.trim().length == 0) {
            ModalManager.show_failure_modal('主菜单名称还未填写！');
            button.removeAttr('disabled');
            return;
        }
        var main_type = $(main_container).attr('data-type');
        var main_value = $(main_container).attr('data-value');
        if (main_type != 'button') {
            var sub_items = $(item).find('.sub-container');
            if (sub_items.length > 0) {
                ModalManager.show_failure_modal('一级菜单添加信息后，不能添加二级菜单！');
                button.removeAttr('disabled');
                return;
            }
            if (main_type == '' || main_value == '') {
                ModalManager.show_failure_modal('一级菜单没有回复内容！');
                button.removeAttr('disabled');
                return;
            }
            var _p = {
                'name': main_name,
                'type': main_type,
                'value': main_value
            }
            result.push(_p);
        } else {
            var _p = {
                'name': main_name,
                'type': 'button'
            }
            var sub_buttons = [];
            var sub_items = $(item).find('.sub-container');
            for (var j = 0; j < sub_items.length; j++) {
                var sub_item = sub_items[j];
                var sub_name = $(sub_item).find('input[name="sub"]').val();
                if (sub_name.trim().length == 0) {
                    ModalManager.show_failure_modal('二级菜单名称不能为空！');
                    button.removeAttr('disabled');
                    return;
                }
                var type = $(sub_item).attr('data-type');
                var value = $(sub_item).attr('data-value');
                if (type == '' || value == '') {
                    ModalManager.show_failure_modal('二级菜单还没有选择回复内容！');
                    button.removeAttr('disabled');
                    return;
                }
                var _sub = {
                    'name': sub_name,
                    'type': type,
                    'value': value
                }
                sub_buttons.push(_sub);
            }
            _p['sub_buttons'] = sub_buttons;
            result.push(_p);
        }
    }
    var data = {
        params: JSON.stringify(result)
    }
    $.ajax({
        type: 'POST',
        url: '/account/' + aid + '/menu',
        data: data,
        success: function (data) {
            button.removeAttr('disabled');
            $('#process-modal').modal('hide');
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
});

function add_fragment() {
    var name = randomString(8);
    var html = '<div class="new-item">' +
        '<div class="input-group">' +
        '<span class="input-group-addon">字段名称</span>' +
        '<input name="iname" type="text" class="form-control" placeholder="填写字段名称">' +
        '</div>' +
        '<div class="input-group form-fragment">' +
        '<span class="input-group-addon">字段类型</span>' +
        '<label>' +
        '<input class="itype" type="radio" value="input" name="' + name + '" checked>' +
        '<span>单行文本</span>' +
        '</label>' +
        '<label>' +
        '<input class="itype" type="radio" value="textarea" name="' + name + '">' +
        '<span>多行文本</span>' +
        '</label>' +
        '</div>' +
        '</div>';
    $('.add-sub-click').before(html);
};

function submit_form() {
    var button = $('#form-save-btn');
    button.attr('disabled', 'disabled');
    var aid = $('input[name="aid"]').val();
    var name = $('input[name="name"]').val();
    if (name == '') {
        button.removeAttr('disabled');
        ModalManager.show_failure_modal('填写表单名称');
        return
    }
    var fragments = $('.new-item');
    if (fragments.length == 1) {
        button.removeAttr('disabled');
        ModalManager.show_failure_modal('至少添加两个字段');
        return
    }
    var params = []
    for (var i = 0; i < fragments.length; i++) {
        var fragment = fragments[i];
        var sub_name = $(fragment).find('input[class="itype"]').attr('name');
        var iname = $(fragment).find('input[name="iname"]').val();
        var itype = $(fragment).find('input[name="' + sub_name + '"]:checked').val();
        if (iname == '' || itype == '' || iname == 'undefined' || itype == 'undefined') {
            button.removeAttr('disabled');
            ModalManager.show_failure_modal('参数不完整');
            return
        }
        var p = {'name': iname, 'type': itype}
        params.push(p);
    }
    var data = {
        'name': name,
        'params': JSON.stringify(params)
    }
    $.ajax({
        type: 'POST',
        url: '/account/' + aid + '/form/new',
        data: data,
        success: function (data) {
            button.removeAttr('disabled');
            if (data.r) {
                ModalManager.show_success_modal('保存成功！');
                setTimeout(function () {
                    window.location = '/account/' + data.aid + '/form'
                }, 1500);
            } else {
                button.removeAttr('disabled');
                ModalManager.show_failure_modal(data.error);
            }
        }
    })
};

function randomString(length) {
    var chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXTZabcdefghiklmnopqrstuvwxyz'.split('');

    if (!length) {
        length = Math.floor(Math.random() * chars.length);
    }

    var str = '';
    for (var i = 0; i < length; i++) {
        str += chars[Math.floor(Math.random() * chars.length)];
    }
    return str;
}
