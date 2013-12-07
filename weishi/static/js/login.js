/*login js in weishi project by shenguan*/

// bind submit handler to #loginForm
$('#loginForm').on('submit', function(e) {
    e.preventDefault(); // prevent native submit
    $(this).ajaxSubmit({
        target: 'myResultsDiv'
    })
});

$('#usernameInput').blur(function(e){
    checkUsername($(e.target),'blur');
});

$('#emailInput').blur(function(e){
    checkEmail($(e.target),'blur');
});

$('#passwordInput').blur(function(e){
    checkPassword($(e.target),'blur');
});

$('#mobileInput').blur(function(e){
    checkMobile($(e.target));
});

// bind submit handler to #signupForm
$('#signupForm').on('submit', function(e) {
    e.preventDefault(); // prevent native submit
    var submitBtn = $('#signupBtn'),
        btnText = '立即注册';
    $(this).ajaxSubmit({
        dataType: 'json',
        beforeSubmit: function(){
            if(!checkUsername($('#usernameInput'),'submit') || !checkEmail($('#emailInput'),'submit') || !checkPassword($('#passwordInput'),'submit') || !checkMobile($('#mobileInput'))){
                return false;
            }
            changeBtnStatus(submitBtn,'loading');
        },
        success: function(data){
            alert(data);
            console.log(data);
        },
        error: function(){
            changeBtnStatus(submitBtn,'normal',btnText);
        }
    })
});

function strlen(str){
    var len = 0;
    for (var i=0; i<str.length; i++) {
        var c = str.charCodeAt(i);
        if ((c >= 0x0001 && c <= 0x007e) || (0xff60<=c && c<=0xff9f)) {
            len++;
        } else {
            len+=2;
        }
    }
    return len;
}

var setInputStatus = function(tg,st,words){
    var setCss = 'form-group clearfix ' + st;
    tg[0].className = setCss;
    tg.find('span').text(words);
}

var changeBtnStatus = function(btn,status,text){
    if(status == 'loading'){
        var btnLoading = '<span class="loading"></span>';
        btn.attr('disabled','disabled').html(btnLoading);
    }else if(status == 'normal'){
        btn.removeAttr('disabled').html(text);
    }
}

var checkInputValue = function(p,tg,ew){
    p._xsrf = getCookie("_xsrf");
    $.ajax({
        type: 'POST',
        url: '/user/check',
        data: p,
        beforeSend: function(){
            setInputStatus(tg,'checking','');
        },
        success: function(data){
            if(data.a == 1){
                setInputStatus(tg,'has-success','可用');
            }else{
                setInputStatus(tg,'has-error',ew);
            }
        }
    });
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

function checkUsername(tg,ac){
    var formGroup = tg.parent(),
        username = tg.val();
    var nameLen = strlen(username);
    if(nameLen > 20){
        setInputStatus(formGroup,'has-error','用户名太长，需要在4-20之间，中文为两个字符！');
        return false;
    }
    if(nameLen > 0 && nameLen < 4){
        setInputStatus(formGroup,'has-error','用户名长度不够，需要在4-20之间，中文为两个字符！');
        return false;
    }
    if(ac == 'blur'){
        if(nameLen == 0 && formGroup.hasClass('has-success')){
            setInputStatus(formGroup,'','');
        }
        if(nameLen >=4 && nameLen<=20){
            var params = {"username" : username};
            checkInputValue(params, formGroup, '用户名已经被占用!');
        }
    }
    if(ac == 'submit' && nameLen == 0){
        setInputStatus(formGroup,'has-error','必填项！');
        return false;
    }
    return true;
}

function checkEmail(tg,ac){
    var formGroup = tg.parent(),
        email = tg.val(),
        re = /^([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$/;
    if(email == ''){
        if(formGroup.hasClass('has-success') && ac == 'blur'){
            setInputStatus(formGroup,'','');
        }
        if(ac == 'submit'){
            setInputStatus(formGroup,'has-error','必填项！');
            return false;
        }
    }else if(!re.test(email)){
        setInputStatus(formGroup,'has-error','邮箱格式不正确！');
        return false;
    }
    if(re.test(email) && ac == 'blur'){
        var params = {"email" : email};
        checkInputValue(params, formGroup, '用户名已经被占用!');
    }
    return true;
}

function checkPassword(tg,ac){
    var formGroup = tg.parent(),
        password = tg.val();
    var passLen = strlen(password);
    if(passLen > 0 && passLen < 6){
        setInputStatus(formGroup,'has-error','密码长度至少6位！');
        return false;
    }else if(ac == 'blur'){
        setInputStatus(formGroup,'','');
    }
    if(ac == 'submit' && passLen == 0){
        setInputStatus(formGroup,'has-error','必填项！');
        return false;
    }
    return true;
}

function checkMobile(tg){
    var formGroup = tg.parent(),
        mobile = tg.val(),
        re = /^1[3|4|5|8][0-9]\d{4,8}$/;
    if(mobile == ''){
        setInputStatus(formGroup,'','');
    }else if(re.test(mobile)){
        setInputStatus(formGroup,'','');
    }else{
        setInputStatus(formGroup,'has-error','请输入正确的手机号！');
        return false;
    }
    return true;
}