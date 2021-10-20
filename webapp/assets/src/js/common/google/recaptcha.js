const r_pub_key = process.env.TS_RECAPTCHA_PUBLIC_KEY;

grecaptcha.ready(function() {
    grecaptcha.execute(r_pub_key, {action:'validate_captcha'})
              .then(function(token) {
        document.getElementById('g-recaptcha-response').value = token;
    });
});
