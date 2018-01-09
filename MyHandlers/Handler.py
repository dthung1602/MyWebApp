import os
from urllib import unquote

import jinja2
import webapp2

handlers = []
template_dir = os.path.join(os.path.dirname(__file__), "../templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)


class Handler(webapp2.RequestHandler):
    page_title = None

    def get_cookie_value(self, cookie_name, default_value=None):
        cookie_value = self.request.cookies.get(cookie_name, None)
        return unquote(cookie_value) if cookie_value else default_value

    def write(self, *args, **kwargs):
        self.response.out.write(*args, **kwargs)
        print "-----------------------------------------------------\n\n"

    def render_str(self, template, **kwargs):
        t = jinja_env.get_template(template)
        __page_title__ = kwargs.get("__page_title__", self.__getattribute__("page_title"))
        return t.render(kwargs, __page_title__=__page_title__)

    def render(self, template, **kwargs):
        self.write(self.render_str(template, **kwargs))

    def error(self, code):
        messages = {
            404: "404 Not Found",
            500: "500 Internal Server Error"
        }
        self.request.status = code
        Handler.render(self, "error.html", __page_title__="Error", error=messages[code])
