function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}


$(function(){
    $("#submit-form").click( function() {
        $('#auth-form').submit();
    });
})

$(function(){
    var uptime = new Date().getTime() / 1000;
    var default_form_head = $("#form-head").html();

    function form_head(data) {
            $("#form-head").html(data).i18n();
    }

    function display_err(i18n_key) {
        form_head('<div class="alert alert-danger err_msg" data-i18n="' + i18n_key + '" role="alert"></div>')
    }

    $('#code').on('input', function() {
        if ($("#form-head").find(".alert").length > 0 ) {
            form_head(default_form_head);
        }
    });

    $("#auth-form").submit(function(e) {
        e.preventDefault();
        form = $(this)

        function acquire() {
            console.log("adquirido");
            $("#code-input").attr('disabled','disabled');
            $("#submit-form").html('<span class="spinner-grow spinner-grow-sm" role="status" aria-hidden="true"></span>'.repeat(3));
        }

        async function chk_uptime() {
            var now = new Date().getTime() / 1000;
            if ((now - uptime) > 240) {
                display_err('csrf_expired');
                await sleep(2000);
                location.reload();
            }
        }

        function release() {
            console.log("liberado");
            $("#code-input").removeAttr('disabled');
            $("#submit-form").html('<span data-i18n="submit"></span>').i18n();
        }

        function redirect(dst) {
            window.location.href = dst;
        }

        function chk_general(value) {
            if (value == 'err_already_auth'){
                redirect('/');
            }
        }

        function chk_code(value) {
            if ((value == 'err_invalid_code') || (value == 'err_expired_code')) {
                display_err('invalid-code');
            }
        }

        function chk_response(data) {
            // nested check
            if (data.success) {
                redirect('/');
            } else {
                if (data['errors']['general']){
                    data['errors']['general'].forEach(element => chk_general(element));
                } else if (data['errors']['code']){
                    data['errors']['code'].forEach(element => chk_code(element));
                }
            }

        }

        function send() {
            var url = form.attr('action');
            var csrf_token = form[0][1].value;

            $.ajax({
               type: "POST",
               url: url,
               contentType: 'application/x-www-form-urlencoded',
               beforeSend: function(xhr, settings) {
                   if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                       xhr.setRequestHeader("X-CSRFToken", csrf_token);
                   }
               },
               data: form.serialize(),
               success: function(data) {
                    chk_response(data);
               }
            });
        }

        function validate() {
            code = form[0][0].value;
            if (code == $.i18n('input-code')) {
                display_err('missing-code');
                return false;
            } else if ( code.length >= 8 && code.length <= 32 ) {
                return true;
            } else {
                display_err('invalid-len');
                return false;
            }
        }

        function main() {
            acquire();
            chk_uptime();
            if (validate()){
                send();
            }
            release();
        }

        main();
    });
 });
