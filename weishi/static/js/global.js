/**
 * Created by young on 14-2-21.
 */

var ModalManager = {

    show_success_modal: function (message) {
        var $modal = $('<div id="save-success" class="modal fade" tablindex="-1" role="dialog" aria-labelledby="myModalLabel" ' +
            'aria-hidden="true">' +
            '<div class="modal-dialog modal-sm">' +
            '<div class="modal-content" style="text-align: center;">' +
            '<span class="glyphicon glyphicon-ok"' +
            ' style="color: #17b385;font-size: 40px;margin: 20px;"></span>' +
            '<div style="margin-bottom: 20px; font-size: 16px; color:#777" class="message"></div>' +
            '</div>' +
            '</div>' +
            '</div>');
        $modal.find('.message').text(message);
        $modal.modal();
        setTimeout(function () {
            $modal.modal('hide');
            $modal.remove();
            $('.modal-backdrop').remove();
        }, 1000)
    },

    show_failure_modal: function (message) {
        var $modal = $('<div id="save-failure" class="modal fade" tablindex="-1" role="dialog" aria-labelledby="myModalLabel" ' +
            'aria-hidden="true">' +
            '<div class="modal-dialog modal-sm">' +
            '<div class="modal-content" style="text-align: center;">' +
            '<span class="glyphicon glyphicon-remove" style="color: #eb6a64;font-size: 40px;margin: 20px;"></span>' +
            '<div style="margin-bottom: 20px; font-size: 16px; color:#777" class="error-message"></div>' +
            '</div>' +
            '</div>' +
            '</div>');
        $modal.find('.error-message').text(message);
        $modal.modal();
        setTimeout(function () {
            $modal.modal('hide')
            $modal.remove();
            $('.modal-backdrop').remove();
        }, 1500)
    },

    show_confirm_modal: function (message, callback) {
        var $modal = $('<div id="confirm-modal" class="modal fade">' +
            '<div class="modal-dialog modal-sm">' +
            '<div class="modal-content" style="text-align: center;">' +
            '<div class="modal-body">' +
            '<span class="glyphicon glyphicon-exclamation-sign" style="color: #eb6a64;font-size: 40px;margin: 20px;"></span>' +
            '<div style="margin-bottom: 20px; font-size: 16px; color:#777" class="error-message"></div>' +
            '</div>' +
            '<div class="modal-footer">' +
            '<button type="button" class="btn btn-default" id="confirm-modal-cancel">取消</button>' +
            '<button type="button" class="btn btn-primary" id="confirm-modal-sure">确定</button>' +
            '</div>' +
            '</div>' +
            '</div>' +
            '</div>');
        $modal.find('.error-message').text(message);
        $modal.modal({
            show: true,
            backdrop: false,
            keyboard: false
        });
        $('#confirm-modal-cancel').click(function () {
            $modal.modal('hide');
            $modal.remove();
            $('.modal-backdrop').remove();
            if (callback) callback(false);
        });
        $('#confirm-modal-sure').click(function () {
            $modal.modal('hide');
            $modal.remove();
            $('.modal-backdrop').remove();
            if (callback) callback(true);
        });
    },

    show_input_modal: function (message, type, callback) {
        var html = '<div id="input-modal" class="modal fade">' +
            '<div class="modal-dialog modal-sm">' +
            '<div class="modal-content">' +
            '<div class="modal-header"><h5 class="modal-title" style="color: #444"></h5></div>' +
            '<div class="modal-body">';
        if (type == 'input') {
            html += '<input class="form-control modal-input" name="input">';
        }
        if (type == 'textarea') {
            html += '<textarea class="form-control modal-input-textarea" name="input"></textarea>';
        }
        html += '<div class="modal-footer">' +
            '<button type="button" class="btn btn-default" id="confirm-modal-cancel">取消</button>' +
            '<button type="button" class="btn btn-primary" id="confirm-modal-sure">确定</button>' +
            '</div>' +
            '</div>' +
            '</div>' +
            '</div>';
        var $modal = $(html);
        $modal.find('.modal-title').text(message);
        $modal.modal({
            show: true,
            backdrop: false,
            keyboard: false
        });
        $('#confirm-modal-cancel').click(function () {
            $modal.modal('hide');
            $modal.remove();
            $('.modal-backdrop').remove();
        });
        $('#confirm-modal-sure').click(function () {
            var input = $modal.find('.form-control').val();
            if (input.trim().length > 0) {
                $modal.modal('hide');
                $modal.remove();
                $('.modal-backdrop').remove();
                if (callback) callback(input);
            }
        });
    }
};