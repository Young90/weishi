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