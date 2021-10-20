$(function(){
    function el(selector) { return document.querySelector(selector) }
    function els(selector) { return document.querySelectorAll(selector) }
    function on(selector, event, action) { els(selector).forEach(e => e.addEventListener(event, action)) }
    function cookie(name) {
      let c = document.cookie.split('; ').find(cookie => cookie && cookie.startsWith(name+'='))
      return c ? c.split('=')[1] : false;
    }

    /* popup button hanler */
    on('.cookie-popup button', 'click', () => {
      el('.cookie-popup').classList.add('cookie-popup--accepted');
      document.cookie = `cookie-accepted=true;samesite=lax;path=/`
    });

    /* popup init hanler */
    if (cookie('cookie-accepted') !== "true") {
      el('.cookie-popup').classList.add('cookie-popup--not-accepted');
    }
})
