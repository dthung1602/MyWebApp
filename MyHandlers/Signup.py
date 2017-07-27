import hmac
import random
import re
import string
import time

from google.appengine.ext import db

import SignIn
from Handler import Handler

USER_RE = re.compile("^[a-zA-Z0-9_-]{3,20}$")
PASS_RE = re.compile("^.{3,20}$")
EMAIL_RE = re.compile("^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


class SignUp(Handler):
    @staticmethod
    def valid_user(username):
        if not USER_RE.match(username):
            return 1
        if User.get_user_by_name(username):
            return 2
        return 0

    @staticmethod
    def valid_pass(password):
        return 0 if PASS_RE.match(password) else 1

    @staticmethod
    def match_pass(password, verify):
        return 0 if password == verify else 1

    @staticmethod
    def valid_email(email):
        return 0 if email == "" or EMAIL_RE.match(email) else 1

    def get(self):
        check = [0, 0, 0, 0]
        self.render("signup.html", check=check)

    def post(self):
        # get info
        username = str(self.request.get("username"))
        password = str(self.request.get("password"))
        verify = str(self.request.get("verify"))
        email = str(self.request.get("email"))

        # validate
        check = [
            self.valid_user(username),
            self.valid_pass(password),
            self.match_pass(password, verify),
            self.valid_email(email)
        ]

        # all valid ?
        all_valid = True if sum(check) == 0 else False

        # perform action
        if all_valid:
            user = User(name=username, password=password, email=email)
            user.put()
            time.sleep(0.5)

            SignIn.set_login_cookie(self, username)
            self.redirect("/welcome")

        else:
            self.render("signup.html", username=username, password=password, verify=verify, email=email, check=check)


class User(db.Model):
    name = db.StringProperty(required=True)
    password = db.StringProperty(required=True)
    email = db.StringProperty()
    salt = db.StringProperty(required=True)
    signup_date = db.DateTimeProperty(auto_now_add=True)
    last_login_date = db.DateTimeProperty(auto_now=True)

    @staticmethod
    def get_user_by_name(username):
        user = db.GqlQuery("SELECT * FROM User WHERE name='%s'" % username).fetch(1)
        return user[0] if len(user) == 1 else None

    @staticmethod
    def create_salt():
        s = string.ascii_letters + string.digits + string.punctuation
        return "".join([random.choice(s) for _ in xrange(10)])

    def __init__(self, *args, **kwargs):
        # for creating new user
        if 'salt' not in kwargs:
            # create salt
            salt = self.create_salt()
            kwargs['salt'] = salt

            # hash password
            kwargs['password'] = self.hash(kwargs['password'], salt)

            # only save email if available
            if kwargs['email'] == "":
                kwargs.pop('email')

        db.Model.__init__(self, *args, **kwargs)

    def hash(self, value, salt=None):
        if salt is None:
            salt = str(self.salt)
        return hmac.new(salt, value).hexdigest()

    def valid_password(self, password):
        print "-------------"
        print password
        print self.password
        print self.hash(password)
        print "\n\n"
        return self.password == self.hash(password)
