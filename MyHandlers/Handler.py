import os
from urllib import unquote

import jinja2
import webapp2

handlers = []
template_dir = os.path.join(os.path.dirname(__file__), "../templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)

__host__ = "http://localhost:8080"
# __host__ = "https://webapp-173414.appspot.com"
# __host__ = "http://  [insert ip address here]  :8080"


class Handler(webapp2.RequestHandler):
    def get_cookie_value(self, cookie_name, default_value=None):
        cookie_value = self.request.cookies.get(cookie_name, None)
        return unquote(cookie_value) if cookie_value else default_value

    def write(self, *args, **kwargs):
        self.response.out.write(*args, **kwargs)
        print "-----------------------------------------------------\n\n"

    def render_str(self, template, **kwargs):
        t = jinja_env.get_template(template)
        __page_title__ = kwargs.get("__page_title__", self.__class__.__name__)
        return t.render(kwargs, __page_title__=__page_title__, __host__=__host__)

    def render(self, template, **kwargs):
        self.write(self.render_str(template, **kwargs))
