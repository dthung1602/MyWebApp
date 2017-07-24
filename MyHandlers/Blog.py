import Handler
from google.appengine.ext import db
import time


class BlogHomePage(Handler.Handler):
    def get(self):
        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created_time DESC limit 10")
        self.render("blog_home_page.html", blogs=blogs)


class NewPostHandler(Handler.Handler):
    def get(self):
        self.render("new_blog_post.html")

    def post(self):
        title = self.request.get("title")
        content = self.request.get("content")

        if not title:
            self.render("new_blog_post.html", content=content, error="Please fill title")
        elif not content:
            self.render("new_blog_post.html", title=title, error="Please fill content")
        else:
            blog = Blog(title=title, content=content)
            blog.put()

            time.sleep(1)
            if Handler.__local__:
                self.redirect("http://localhost:8080/blog")
            else:
                self.redirect("https://webapp-173414.appspot.com/blog")


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
        return t.render(blog=self, blog_id=blog_id, full=full, local=Handler.__local__)

    def render_content(self):
        return self.content.replace("\n", "<br>")
