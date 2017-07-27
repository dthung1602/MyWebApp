import hmac

import Handler
import Signup

SECRET = "X`e:CA^$PWm;vvj'=]Jv]O7>dG9H&V8Exq0F!S`Ha{Wa9z6?CR"


def make_secure(value):
    value = str(value)
    hashed_value = str(hmac.new(SECRET, value).hexdigest())
    return value + '|' + hashed_value


def set_login_cookie(handler, username):
    user_cookie = make_secure(username)
    handler.response.headers.add_header('Set-Cookie', 'user=%s' % user_cookie)


class SignIn(Handler.Handler):
    def get(self):
        self.render("signin.html")

    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")
        user = Signup.User.get_user_by_name(username)

        if not user:
            self.render("signin.html", username_error="Invalid user name")
            return

        if not user.valid_password(password):
            self.render("signin.html", password_error="Invalid password")
            return

        set_login_cookie(self, username)
        self.redirect("/welcome")
