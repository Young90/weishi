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