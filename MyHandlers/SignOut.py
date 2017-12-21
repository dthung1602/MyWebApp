import Handler


def reset_login_cookie(handler):
    handler.response.delete_cookie('user')


class SignOut(Handler.Handler):
    page_title = "Sign out"

    def get(self):
        reset_login_cookie(self)
        self.redirect("/signin")
