/**
 * Created by young on 14-2-21.
 */

var ModalManager = {

    show_success_modal: function (message) {
        var $success_modal = $('<div id="save-success" class="modal fade" tablindex="-1" role="dialog" aria-labelledby="myModalLabel" ' +
            'aria-hidden="true">' +
            '<div class="modal-dialog modal-sm">' +
            '<div class="modal-content" style="text-align: center;">' +
            '<span class="glyphicon glyphicon-ok"' +
            ' style="color: #17b385;font-size: 40px;margin: 20px;"></span>' +
            '<div style="margin-bottom: 20px; font-size: 16px; color:#777">' + message + '</div>' +
            '</div>' +
            '</div>' +
            '</div>');
        $success_modal.modal();
        setTimeout(function () {
            $success_modal.modal('hide')
        }, 1000)
    },

    show_failure_modal: function (message) {
        var $failure_modal = $('<div id="save-failure" class="modal fade" tablindex="-1" role="dialog" aria-labelledby="myModalLabel" ' +
            'aria-hidden="true">' +
            '<div class="modal-dialog modal-sm">' +
            '<div class="modal-content" style="text-align: center;">' +
            '<span class="glyphicon glyphicon-remove" style="color: #eb6a64;font-size: 40px;margin: 20px;"></span>' +
            '<div style="margin-bottom: 20px; font-size: 16px; color:#777" class="error-message">' + message + '</div>' +
            '</div>' +
            '</div>' +
            '</div>');
        $failure_modal.modal();
        setTimeout(function () {
            $failure_modal.modal('hide')
        }, 1500)
    },

    show_confirm_modal: function (message, proxy) {
        var $confirm_modal = $('<div id="confirm-modal" class="modal fade">' +
            '<div class="modal-dialog">' +
            '<div class="modal-content" style="text-align: center;">' +
            '<div class="modal-body">' +
            '<span class="glyphicon glyphicon-exclamation-sign" style="color: #eb6a64;font-size: 40px;margin: 20px;"></span>' +
            '<div style="margin-bottom: 20px; font-size: 16px; color:#777" class="error-message">' + message + '</div>' +
            '</div>' +
            '<div class="modal-footer">' +
            '<button type="button" class="btn btn-default" data-dismiss="modal">取消</button>' +
            '<button type="button" class="btn btn-primary" id="confirm-modal-sure" onclick="javascript:after_click(proxy);">确定</button>' +
            '</div>' +
            '</div>' +
            '</div>' +
            '</div>');
        $confirm_modal.modal();
    }

};

function after_click(proxy) {
    proxy();
}