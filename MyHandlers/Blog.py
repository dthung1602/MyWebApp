import time
from urllib import quote

from google.appengine.ext import db

import Handler
import Welcome

BLOG_ADMIN_GROUP = [
    "admin",
    "hung",
]


class BlogHomePage(Handler.Handler):
    def get(self):
        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created_time DESC limit 10")
        self.render("blog_home_page.html", blogs=blogs)


def log_in_as_admin(cookie):
    username = cookie.split('|')[0]
    return Welcome.valid_login_cookie(cookie) and username in BLOG_ADMIN_GROUP


class NewPostHandler(Handler.Handler):
    def get(self):
        cookie = self.get_cookie_value('user')

        if cookie:
            if log_in_as_admin(cookie):
                self.render("new_blog_post.html")
            else:
                self.response.set_cookie("general_signin_errors", quote("You are not administrator!"))
                self.response.set_cookie("redirect", "/blog/newpost")
                self.redirect("/signin")
        else:
            self.response.set_cookie("general_signin_errors",
                                     quote("You must sign in as administrator to create new blog!"))
            self.response.set_cookie("redirect", "/blog/newpost")
            self.redirect("/signin")

    def post(self):
        title = self.request.get("title")
        content = self.request.get("content")
        cookie = self.get_cookie_value('user')

        if cookie:
            if log_in_as_admin(cookie):
                if not title:
                    self.render("new_blog_post.html", content=content, error="Please fill title")
                elif not content:
                    self.render("new_blog_post.html", title=title, error="Please fill content")
                else:
                    blog = Blog(title=title, content=content)
                    blog.put()

                    time.sleep(1)
                    self.redirect(Handler.__host__ + "/blog")
            else:
                self.response.set_cookie("general_signin_errors", quote("You are not administrator!"))
                self.response.set_cookie("redirect", "/blog/newpost")
                self.redirect("/signin")
        else:
            self.response.set_cookie("general_signin_errors",
                                     quote("You must sign in as administrator to create new blog!"))
            self.response.set_cookie("redirect", "/blog/newpost")
            self.redirect("/signin")


class BlogHandler(Handler.Handler):
    def get(self, blog_id):
        blog = Blog.get_by_id(int(blog_id))
        self.render("blog.html", blog=blog)


class Blog(db.Model):
    title = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created_time = db.DateTimeProperty(auto_now_add=True)
    last_modified = db.DateTimeProperty(auto_now=True)

    def get_description(self):
        return " ".join(self.content.split()[:35]) + " ..."

    def render_html(self, full=True):
        t = Handler.jinja_env.get_template("single_blog.html")
        blog_id = self.key().id()
        return t.render(blog=self, blog_id=blog_id, full=full, __host__=Handler.__host__)

    def render_content(self):
        return self.content.replace("\n", "<br>")
