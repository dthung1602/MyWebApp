from google.appengine.ext import db

import SignOut
import Signup
from Handler import Handler


class Welcome(Handler):
    def get(self):
        user_cookie_str = self.request.cookies.get("user", None)

        if not user_cookie_str:
            self.redirect("/signup")
        else:
            tmp = user_cookie_str.split('|')
            username = tmp[0].encode("utf8")
            hash_value = tmp[1].encode("utf8")

            user = db.GqlQuery("SELECT * FROM User WHERE name ='%s'" % username).fetch(1)
            if len(user) == 0:
                SignOut.SignOut.reset_user_cookie(self)
                self.redirect("/signup")
                return

            user = user[0]
            if hash_value == Signup.User.hash(username, user.salt.encode('utf8')):
                self.render("welcome.html", user=username)
            else:
                self.redirect("/signup")
