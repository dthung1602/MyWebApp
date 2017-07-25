import Handler
from google.appengine.ext import db


class SignOut(Handler.Handler):
    @staticmethod
    def reset_user_cookie(web):
        web.response.headers['Set-Cookie'] = "user="

    def get(self):
        SignOut.reset_user_cookie(self)
        self.redirect("/signin")
