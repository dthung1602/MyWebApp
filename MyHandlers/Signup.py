from Handler import Handler
import re
from google.appengine.ext import db
import hmac
import string
import random
import time
import unicodedata

USER = re.compile("^[a-zA-Z0-9_-]{3,20}$")
PASS = re.compile("^.{3,20}$")
EMAIL = re.compile("^[\S]+@[\S]+.[\S]+$")


class SignUp(Handler):

    @staticmethod
    def valid_user(username):
        if not USER.match(username):
            return 1
        user = db.GqlQuery("SELECT * FROM User WHERE name = '%s'" % username).fetch(1)
        if len(user) > 0:
            return 2
        return 0

    @staticmethod
    def valid_pass(password):
        return 0 if PASS.match(password) else 1

    @staticmethod
    def match_pass(password, verify):
        return 0 if password == verify else 1

    @staticmethod
    def valid_email(email):
        return 0 if email == "" or EMAIL.match(email) else 1

    def get(self):
        check = [0, 0, 0, 0]
        username = password = verify = email = ""
        self.render("signup.html", username=username,
                    password=password, verify=verify, email=email, check=check)

    def post(self):
        # get info
        username = self.request.get("username").encode("utf8")
        password = self.request.get("password").encode("utf8")
        verify = self.request.get("verify").encode("utf8")
        email = self.request.get("email").encode("utf8")

        # validate
        check = [
            self.valid_user(username),
            self.valid_pass(password),
            self.match_pass(password, verify),
            self.valid_email(email)
        ]

        # all valid ?
        valid = True if sum(check) == 0 else False
        
        # perform action
        if valid:
            hashed_password, salt = User.create_password_and_salt(password)
            user = User(name=username, password=hashed_password, salt=salt)
            user.put()
            time.sleep(0.5)

            user_cookie = user.name + '|' + user.hash(user.name, user.salt)
            self.response.headers.add_header(
                'Set-Cookie', 'user=%s' % user_cookie)
            self.redirect("/welcome")
        else:
            self.render("signup.html",
                        username=username.decode('utf8'),
                        password=password.decode('utf8'),
                        verify=verify.decode('utf8'),
                        email=email.decode('utf8'),
                        check=check)
            


class User(db.Model):
    name = db.StringProperty(required=True)
    password = db.StringProperty(required=True)
    salt = db.StringProperty(required=True)
    signup_date = db.DateTimeProperty(auto_now_add=True)
    last_login_date = db.DateTimeProperty(auto_now=True)

    @staticmethod
    def hash(value, salt):
        return hmac.new(salt, value).hexdigest()

    @staticmethod
    def create_salt():
        s = string.ascii_letters + string.digits + string.punctuation
        return "".join([random.choice(s) for i in xrange(10)])

    @staticmethod
    def create_password_and_salt(password):
        salt = User.create_salt()
        return User.hash(password, salt), salt

    def valid_password(self, password):
        return self.password == User.hash(password, self.salt.encode('utf8'))
