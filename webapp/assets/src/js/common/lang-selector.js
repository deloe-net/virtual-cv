$(function(){
    $('#lang-selector').change(function(){
            var lang = $(this).val();
            document.cookie = "locale=" + lang + ";samesite=lax;path=/";
            console.log(lang);
            $('html').attr("lang", lang)
            $.i18n({ locale: lang});
            $("body").i18n();
            $("head").i18n();
    });
});
