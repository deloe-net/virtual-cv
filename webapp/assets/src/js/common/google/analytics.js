const g_id = process.env.TS_G_ANALYTICS_ID;
window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}
gtag('js', new Date());
gtag('config', g_id);
