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
    var id = $('input[name=id]').val();
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
        'id': id,
        'title': title,
        'summary': summary,
        'link': link,
        'image': thumb
    }
    $.ajax({
        type: 'POST',
        url: window.location.href,
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
    var params = [];
    for (var i = 0; i < items.length; i++) {
        var item = $(items[i]);
        var id = item.find('input[name=id]').val();
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
            'id': id,
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
        type: 'POST',
        url: window.location.href,
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

function initial_upload() {
       var url = '/upload';
        $('.fileupload').each(function (input_index) {
            $(this).fileupload({
                dropZone: $(this),
                url: url,
                dataType: 'json',
                done: function (e, data) {
                    $.each(data.result.files, function (index, file) {
                        var zone = $('.files')[input_index];
                        var html = '<div class="img-container" data-href="' + file.url +
                                '"><a class="img-result" href="' + file.url +
                                '" target="_blank"><img src="' + file.thumbnailUrl +
                                '"><p>图片</p></a><p class="fa fa-minus-circle rm"></p></div>';
                        $(zone).append(html);
                        var pro_zone = $('.progress')[input_index];
                        $(pro_zone).removeClass('progress-striped active');
                    });
                },
                progressall: function (e, data) {
                    var progress = parseInt(data.loaded / data.total * 100, 10);
                    var pro_zone = $('.progress .progress-bar')[input_index]
                    $(pro_zone).css(
                            'width',
                            progress + '%'
                    );
                }
            }).prop('disabled', !$.support.fileInput)
                    .parent().addClass($.support.fileInput ? undefined : 'disabled');
        });
    }

function add_sub_site_link(e) {
    var html = '<div class="new-item ll">' +
        '<input type="hidden" name="id" value="0">' +
        '<div class="input-group edit-group">' +
        '<span class="input-group-addon">标题</span>' +
        '<input name="title" type="text" class="form-control" placeholder="标题字数要少于30">' +
        '</div>' +
        '<div class="input-group edit-group">' +
        '<span class="input-group-addon">链接</span>' +
        '<input name="link" type="text" class="form-control" placeholder="以http://开头">' +
        '</div>' +
        '<div class="btn btn-success fileinput-button">' +
        '<i class="glyphicon glyphicon-plus"></i>' +
        '<span>选择缩略图 <span class="tip">(建议图片尺寸640x360，大小控制在500Kb以内)</span></span>' +
        '<input class="fileupload" type="file" name="file">' +
        '</div>' +
        '<div class="progress progress-striped active">' +
        '<div class="progress-bar progress-bar-success"></div>' +
        '</div>' +
        '<div class="files"></div>' +
        '</div>';
    $(e).before(html);
    initial_upload();
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
    var thumb_container = $('div.thumb > div.img-container');
    var thumb = '';
    if (thumb_container.length > 0) {
        thumb = thumb_container.data('href');
    }
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
    var img_containers = $('div.focus > div.img-container');
    var images = [];
    for (var i = 0; i< img_containers.length; i++) {
        images.push($(img_containers[i]).data('href'));
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
        ModalManager.show_failure_modal('请添加导航!');
        return false;
    }
    var ps = {thumb: thumb, title: title, phone: phone, images: images, links:ls};
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
                ModalManager.show_failure_modal(data.e);
            }
        }
    })
}

function save_site_list(e) {
    $(e).attr('disabled', 'disabled');
    var aid = $('input[name=aid]').val();
    var type = $('input[name=type]:checked').val();
    var title = $('input[name=title]').val();
    var main_thumb = $('.main_thumb').find('.img-container').data('href');
    var ll_list = $('.ll');
    var p_list = [];
    for (var i = 0;i < ll_list.length; i++) {
        var ll = $(ll_list[i]);
        var l_title = ll.find('input[name=title]').val();
        var l_link = ll.find('input[name=link]').val();
        var l_thumb = ll.find('.img-container').data('href');
        var p_l = {title: l_title, link: l_link, thumb: l_thumb}
        p_list.push(p_l);
    }
    var params = {type: type, title: title, thumb: main_thumb, lists: p_list};
    $.ajax({
        type: 'POST',
        url: window.location.href,
        data: {params:JSON.stringify(params)},
        success: function(data) {
            $(e).removeAttr('disabled');
            if (data.r) {
                ModalManager.show_success_modal('保存成功！')
                setTimeout(function () {
                    window.location = window.location.href + '/list';
                }, 1500);
            } else {
                ModalManager.show_failure_modal(data.e);
            }
        }
    })
}