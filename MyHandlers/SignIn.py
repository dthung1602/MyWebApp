import Handler
from google.appengine.ext import db


class SignIn(Handler.Handler):
    def get(self):
        self.render("signin.html")

    def post(self):
        username = self.request.get("username").encode("utf8")
        password = self.request.get("password").encode("utf8")
        user = db.GqlQuery("SELECT * FROM User WHERE name = '%s'" % username).fetch(1)

        if len(user) == 0:
            self.render("signin.html", username_error="Invalid user name")
            return
        
        user = user[0]
        if not user.valid_password(password):
            self.render("signin.html", password_error="Invalid password")
            return

        user_cookie = username + '|' + user.hash(username, user.salt.encode("utf8"))
        self.response.headers.add_header(
                'Set-Cookie', 'user=%s' % user_cookie)
        self.redirect("/welcome")
        
