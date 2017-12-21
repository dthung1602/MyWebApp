import time

from google.appengine.ext import db

import Handler


class AsciiArt(Handler.Handler):
    page_title = "Ascii Art"
    
    def render_page(self, title="", art="", error=""):
        arts = db.GqlQuery("SELECT * FROM Art ORDER BY time_created DESC")
        self.render("ascii_art.html", title=title, art=art, error=error, arts=arts)

    def get(self):
        self.render_page()

    def post(self):
        title = self.request.get("title")
        art = self.request.get("art")

        if title and art:
            ascii_art = Art(title=title, art=art)
            ascii_art.put()
            time.sleep(0.2)
            self.redirect("/ascii_art")
        else:
            self.render_page(title, art, "Please fill title and art!")


class Art(db.Model):
    title = db.StringProperty(required=True)
    art = db.TextProperty(required=True)
    time_created = db.DateTimeProperty(auto_now_add=True)
