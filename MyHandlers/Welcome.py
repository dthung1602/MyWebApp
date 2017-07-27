import SignIn
import Signup
from Handler import Handler


def valid_login_cookie(cookie):
    username = cookie.split('|')[0]
    return cookie == SignIn.make_secure(username) and Signup.User.get_user_by_name(username)


class Welcome(Handler):
    def get(self):
        login_cookie = self.request.cookies.get("user", None)

        if not login_cookie or not valid_login_cookie(login_cookie):
            self.redirect("/signup")
        else:
            username = login_cookie.split('|')[0]
            self.render("welcome.html", user=username)
