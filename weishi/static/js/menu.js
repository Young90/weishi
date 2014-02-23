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
        '<span class="action"><a href="javascript:;">文本</a></span>' +
        '<span class="action"><a href="javascript:;">单条图文</a></span>' +
        '<span class="action"><a href="javascript:;">多条图文</a></span>' +
        '<span class="action"><a href="javascript:;">链接</a></span>' +
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
    var items = $(container).find('.sub-container');
    if (items.length >= 5) {
        ModalManager.show_failure_modal('二级菜单最多五个！');
        return;
    }
    var sub_html = '<div class="sub-container" data-type="" data-value="">' +
        '<div class="input-container">' +
        '<input type="text" name="main" class="form-control input-lg main" placeholder="二级菜单名称">' +
        '<span class="result"></span>' +
        '</div>' +
        '<div class="op">' +
        '<span class="action black">回复内容 </span>' +
        '<span class="action"><a href="javascript:;" onclick="javascript:show_input_text_dialog(this);">文本</a></span>' +
        '<span class="action"><a href="javascript:;">单条图文</a></span>' +
        '<span class="action"><a href="javascript:;">多条图文</a></span>' +
        '<span class="action"><a href="javascript:;">链接</a></span>' +
        '<span class="action remove"><a href="javascript:;" onclick="javascript:remove_sub_menu(this);">删除</a></span>' +
        '</div>' +
        '</div>';
    var main = $(container).find('.menu-item');
    $(main).append(sub_html);
}

function remove_sub_menu(obj) {
    var container = $(obj).parents('.sub-container');
    ModalManager.show_confirm_modal('确定移除此二级菜单吗？', function (result) {
        if (result) $(container).remove();
    });
}

function remove_main_menu(obj) {
    var container = $(obj).parents('.edit-menu');
    ModalManager.show_confirm_modal('所有的二级菜单也将移除，确定吗？', function (result) {
        if (result) $(container).remove();
    });
}

function show_input_text_dialog(obj) {
    ModalManager.show_input_modal('输入要回复的文本信息', function (input) {
        var container = $(obj).parents('.op').parent();
        var result = $(container).find('.result');
        $(container).attr('data-type', 'text');
        $(container).attr('data-value', input);
        $(result).text('文本：' + input);
    });
}