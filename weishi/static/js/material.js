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
        alert('参数不正确');
        return;
    }
    if (title == '') {
        alert('填写标题！');
        return;
    }
    if (content == '') {
        alert('内容不能为空！');
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
                $('#save-success').modal();
                setTimeout(function () {
                    $('#save-success').modal('hide')
                }, 1000);
                setTimeout(function () {
                    window.location = '/account/' + data.aid + '/article'
                }, 1500);
            }
        }
    })
});


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
        alert('标题不能为空！');
        button.removeAttr('disabled');
        return
    }
    if (summary == '') {
        alert('摘要不能为空！');
        button.removeAttr('disabled');
        return
    }
    if (link == '') {
        alert('链接不能为空！');
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
        type:'POST',
        url:'/account/' + aid + '/image_article/new/single',
        data: params,
        success:function(data) {
            if (data.r) {
                $('#save-success').modal();
                setTimeout(function () {
                    $('#save-success').modal('hide')
                }, 1000);
                setTimeout(function () {
                    window.location = '/account/' + data.aid + '/image_article'
                }, 1500);
            } else {
                button.removeAttr('disabled');
                $('.error-message').html(data.error);
                $('#save-failure').modal();
                setTimeout(function () {
                    $('#save-failure').modal('hide')
                }, 1300);
            }
        }
    })
})