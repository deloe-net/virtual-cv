from flask import render_template


def generic_err(page_code):
    return (
        render_template('errors/index.html',
                        page_code=page_code,
                        bp_name='errors'),
        page_code)


def page_not_found(e):
    return generic_err(404)


def forbidden(e):
    return generic_err(403)


__all__ = ['page_not_found', 'forbidden']
