from flask import redirect
from flask import render_template
from flask import url_for

from .index import bp_frontend_auth
from webapp.settings import settings_pool


@bp_frontend_auth.route('/oauth', methods=['GET'])
def oauth_page():
    if settings_pool.auth.code_supply_method == 'oauth-auto':
        return redirect(url_for('frontend_home.home_page'))
    else:
        return render_template('auth/oauth.html')
