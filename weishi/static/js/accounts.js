/*accounts js in weishi project by shenguan*/

// bind submit handler to #addAccountForm
$('#addAccountForm').on('submit', function(e) {
    e.preventDefault(); // prevent native submit
    var submitBtn = $('#addAccountBtn'),
        btnText = '添加';
    $(this).ajaxSubmit({
        dataType: 'json',
        beforeSubmit: function(){
            if(checkInputsEmpty()){
                return false;
            }
            changeBtnStatus(submitBtn,'loading');
        },
        success: function(data){
            if(data.r == 1){
                //window.location.href = '/';
            }else{
                $('.alert-danger').text(data.error).fadeIn();
                changeBtnStatus(submitBtn,'normal',btnText);
            }
        },
        error: function(){
            $('.alert-danger').text('网络出错，添加失败，请重试！').fadeIn();
            changeBtnStatus(submitBtn,'normal',btnText);
        }
    })
});

var changeBtnStatus = function(btn,status,text){
    if(status == 'loading'){
        var btnLoading = '<span class="loading"></span>';
        btn.attr('disabled','disabled').html(btnLoading);
    }else if(status == 'normal'){
        btn.removeAttr('disabled').html(text);
    }
}

function checkInputsEmpty(){
    var hasEmpty = false;
    $('.form-control').each(function(){
        var _target = $(this);
        if(_target.val() == ''){
            _target.parent().addClass('has-error');
            hasEmpty = true;
        }else{
            _target.parent().removeClass('has-error');
        }
    });
    $('.alert-danger').fadeOut();
    return hasEmpty;
}