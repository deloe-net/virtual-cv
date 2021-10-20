from .frontent import forbidden
from .frontent import page_not_found
from webapp.webapp import core


core.register_error_handler(404, page_not_found)
core.register_error_handler(403, forbidden)
