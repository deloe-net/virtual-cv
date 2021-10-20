import es from 'locales/es.json';
import en from 'locales/en.json';
import ja from 'locales/ja.json';


jQuery(document).ready(function (e) {
    e.i18n.debug = !0;
    var default_lang = $('html').attr("lang");
    var r = e.i18n({locale: default_lang});

    r.load({
        'es': es,
        'en': en,
        'ja': ja
    }).done(
        function () {
                e("body").i18n()
                e("head").i18n()
                }
    );
});
