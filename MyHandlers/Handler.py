import os
from urllib import unquote

import jinja2
import webapp2

handlers = []
template_dir = os.path.join(os.path.dirname(__file__), "../templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)

# local = True means http://localhost:8080/
# local = False means https://webapp-173414.appspot.com/

__local__ = True


class Handler(webapp2.RequestHandler):
    def get_cookie_value(self, cookie_name, default_value=None):
        cookie_value = self.request.cookies.get(cookie_name, None)
        return unquote(cookie_value) if cookie_value else default_value

    def write(self, *args, **kwargs):
        self.response.out.write(*args, **kwargs)
        print "-----------------------------------------------------\n\n"

    def render_str(self, template, **kwargs):
        t = jinja_env.get_template(template)
        _page_title = self.__class__.__name__
        return t.render(kwargs, _page_title=_page_title, local=__local__)

    def render(self, template, **kwargs):
        self.write(self.render_str(template, **kwargs))
