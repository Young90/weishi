/*
 保存新创建的文章
 */
$('#article-save-btn').on('click', function (e) {
    var button = $('#article-save-btn');
    button.attr('disabled', 'disabled');
    var form = $('.post-form');
    var aid = $(form).find('input[name="aid"]').val();
    var title = $(form).find('input[name="title"]').val();
    var content = UE.getEditor('content').getContent();
    if (aid == '') {
        ModalManager.show_failure_modal('参数不正确！');
        button.removeAttr('disabled');
        return;
    }
    if (title == '') {
        ModalManager.show_failure_modal('填写标题！');
        button.removeAttr('disabled');
        return;
    }
    if (content == '') {
        ModalManager.show_failure_modal('内容不能为空！');
        button.removeAttr('disabled');
        return;
    }
    var params = {
        "title": title,
        "content": content
    }
    $.ajax({
        type: 'POST',
        url: '/account/' + aid + '/article/new',
        data: params,
        success: function (data) {
            if (data.r) {
                ModalManager.show_success_modal('保存成功！');
                setTimeout(function () {
                    window.location = '/account/' + data.aid + '/article'
                }, 1500);
            }
        }
    })
});

/*
 更新文章信息
 */
$('#article-update-btn').on('click', function (e) {
    var button = $('#article-update-btn');
    button.attr('disabled', 'disabled');
    var form = $('.post-form');
    var aid = $(form).find('input[name="aid"]').val();
    var slug = $(form).find('input[name="slug"]').val();
    var title = $(form).find('input[name="title"]').val();
    var content = UE.getEditor('content').getContent();
    if (aid == '') {
        ModalManager.show_failure_modal('参数不正确！');
        button.removeAttr('disabled');
        return;
    }
    if (title == '') {
        ModalManager.show_failure_modal('填写标题！');
        button.removeAttr('disabled');
        return;
    }
    if (content == '') {
        ModalManager.show_failure_modal('内容不能为空！');
        button.removeAttr('disabled');
        return;
    }
    var params = {
        "slug": slug,
        "title": title,
        "content": content
    }
    $.ajax({
        type: 'POST',
        url: '/account/' + aid + '/article/' + slug + '/edit',
        data: params,
        success: function (data) {
            if (data.r) {
                ModalManager.show_success_modal('保存成功！');
                setTimeout(function () {
                    window.location = '/account/' + data.aid + '/article'
                }, 1500);
            }
        }
    })
});

/*
 删除文章
 */
function delete_article(aid, slug) {
    ModalManager.show_confirm_modal('确认删除？', function (result) {
        if (result) {
            $.ajax({
                type: 'DELETE',
                url: '/account/' + aid + '/article/' + slug + '/edit',
                success: function (data) {
                    if (data.r) {
                        ModalManager.show_success_modal('保存成功！');
                        setTimeout(function () {
                            window.location = '/account/' + data.aid + '/article'
                        }, 1500);
                    }
                }
            })
        }
    });
};

/*
 保存单条图文消息
 */
$('#single-save-btn').on('click', function (e) {
    var button = $('#single-save-btn');
    button.attr('disabled', 'disabled');
    var aid = $('input[name="aid"]').val();
    var title = $('input[name="title"]').val();
    var summary = $('textarea[name="summary"]').val();
    var link = $('input[name="link"]').val();

    if (title == '') {
        ModalManager.show_failure_modal('标题不能为空！');
        button.removeAttr('disabled');
        return
    }
    if (summary == '') {
        ModalManager.show_failure_modal('摘要不能为空！');
        button.removeAttr('disabled');
        return
    }
    if (link == '') {
        ModalManager.show_failure_modal('链接不能为空！');
        button.removeAttr('disabled');
        return;
    }
    var files = $('#files').find('a[href]');
    var thumb = '';
    if (files.length > 0) {
        thumb = $(files[0]).attr('href');
    }
    if (thumb == '') {
        var flag = confirm('确定不添加封面？');
        if (!flag) {
            button.removeAttr('disabled');
            return;
        }
    }
    var params = {
        'title': title,
        'summary': summary,
        'link': link,
        'image': thumb
    }
    $.ajax({
        type: 'POST',
        url: '/account/' + aid + '/image_article/new/single',
        data: params,
        success: function (data) {
            if (data.r) {
                ModalManager.show_success_modal('保存成功！');
                setTimeout(function () {
                    window.location = '/account/' + data.aid + '/image_article/single'
                }, 1500);
            } else {
                button.removeAttr('disabled');
                ModalManager.show_failure_modal(data.error);
            }
        }
    })
})

/*
 保存多条图文消息
 */
$('#multi-save-btn').on('click', function (e) {
    var button = $('#multi-save-btn');
    button.attr('disabled', 'disabled');
    var aid = $('input[name="aid"]').val();
    var items = $('.new-item');
    var params = []
    for (var i = 0; i < items.length; i++) {
        var item = $(items[i]);
        var title = item.find('input[name="title"]').val();
        var link = item.find('input[name="link"]').val();
        var image_link = item.find('a[href]');
        var image = '';
        if (image_link.length > 0) {
            image = item.find('a[href]').attr('href');
        }
        if (title == '') {
            continue;
        }
        var _p = {
            'title': title,
            'link': link,
            'image': image
        }
        params.push(_p);
    }
    if (params.length == 0) {
        button.removeAttr('disabled');
        ModalManager.show_failure_modal('请填写正确的参数');
        return;
    }
    var data = {
        params: JSON.stringify(params)
    }
    $.ajax({
        type: "POST",
        url: "/account/" + aid + '/image_article/new/multi',
        data: data,
        success: function (data) {
            button.removeAttr('disabled');
            if (data.r) {
                ModalManager.show_success_modal('保存成功！')
                setTimeout(function () {
                    window.location = '/account/' + data.aid + '/image_article/multi'
                }, 1500);
            } else {
                button.removeAttr('disabled');
                ModalManager.show_failure_modal(data.error);
            }
        }
    })
});

function delete_material(type, id) {
    // 删除图文消息
    var aid = $.cookie('aid');
    ModalManager.show_confirm_modal('确定删除？', function(result) {
        if (!result) {
            return;
        }
        $.ajax({
            type:'POST',
            url: '/account/' + aid + '/delete_material',
            data: {type: type, id: id},
            success: function(data) {
                if (data.r) {
                    window.location.reload();
                } else {
                    ModalManager.show_failure_modal(data.error);
                }
            }
        })
    })
}

function add_site_link(e) {
    var html = '<div class="input-group edit-group links">' +
        '<p class="fa fa-minus-circle rm-n"></p>' +
        '<input name="name" type="text" class="form-control site-ipt-s" placeholder="导航名称">' +
        '<input name="icon" type="text" class="form-control site-ipt-s" placeholder="导航图标">' +
        '<input name="link" type="text" class="form-control site-ipt-l" placeholder="地址链接">' +
        '</div>';
    $(e).before(html);
}

$(document).on('click', 'p.rm, p.rm-n', function(){
    var that = $(this);
    ModalManager.show_confirm_modal('确定删除吗？', function(result){
        if (result) {
            var target = that.parent();
            target.remove();
        }
    })
} );

function save_site(e) {
    $(e).attr('disabled', 'disabled');
    var aid = $('input[name=aid]').val();
    var title = $('input[name=title]').val();
    if (title == '') {
        $(e).removeAttr('disabled');
        ModalManager.show_failure_modal('输入标题!');
        return false;
    }
    var phone = $('input[name=phone]').val();
    if (phone == '') {
        $(e).removeAttr('disabled');
        ModalManager.show_failure_modal('输入电话!');
        return false;
    }
    var img_containers = $('.img-result');
    var images = [];
    for (var i = 0; i< img_containers.length; i++) {
        images.push($(img_containers[i]).attr('href'));
    }
    if (images.length == 0) {
        $(e).removeAttr('disabled');
        ModalManager.show_failure_modal('请上传焦点图!');
        return false;
    }
    var links = $('.links');
    var ls = [];
    for (var i = 0; i < links.length; i++) {
        var c = $(links[i]);
        var name = c.find('input[name=name]').val();
        var icon = c.find('input[name=icon]').val();
        var link = c.find('input[name=link]').val();
        if (name != '' && icon != '' && link != '') {
            var p = {name: name, icon: icon, link: link};
            ls.push(p);
        }
    }
    if (ls.length == 0) {
        $(e).removeAttr('disabled');
        ModalManager.show_failure_modal('请上传焦点图!');
        return false;
    }
    var ps = {title: title, phone: phone, images: images, links:ls}
    $.ajax({
        url: '/account/' + aid + '/site',
        type: 'POST',
        data: {params:JSON.stringify(ps)},
        success: function(data) {
            $(e).removeAttr('disabled');
            if (data.r) {
                ModalManager.show_success_modal('保存成功！')
                setTimeout(function () {
                    window.location.reload();
                }, 1500);
            } else {
                ModalManager.show_failure_modal(data.error);
            }
        }
    })
}