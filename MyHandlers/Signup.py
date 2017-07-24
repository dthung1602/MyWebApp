from Handler import Handler
import re

USER = re.compile("^[a-zA-Z0-9_-]{3,20}$")
PASS = re.compile("^.{3,20}$")
EMAIL = re.compile("^[\S]+@[\S]+.[\S]+$")


class SignUp(Handler):

    @staticmethod
    def valid_user(username):
        return USER.match(username)

    @staticmethod
    def valid_pass(password):
        return PASS.match(password)

    @staticmethod
    def match_pass(password, verify):
        return password == verify

    @staticmethod
    def valid_email(email):
        return email == "" or EMAIL.match(email)

    def get(self):
        check = [True, True, True, True]
        username = password = verify = email = ""
        self.render("signup.html", username=username,
                    password=password, verify=verify, email=email, check=check)

    def post(self):
        # get info
        username = self.request.get("username")
        password = self.request.get("password")
        verify = self.request.get("verify")
        email = self.request.get("email")

        # validate
        check = [
            self.valid_user(username),
            self.valid_pass(password),
            self.match_pass(password, verify),
            self.valid_email(email)
        ]

        # all valid ?
        valid = True
        for c in check:
            valid = valid and c
        print "--------------------ok-----------------------"
        # perform action
        if not valid:
            self.render("signup.html", username=username,
                        password=password, verify=verify, email=email, check=check)
        else:
            self.redirect("/welcome?user=%s" % username)
