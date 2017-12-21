import hmac

from Handler import Handler

SECRET = "blah blah blah"


class Test(Handler):
    page_title = "Test cookie"

    @staticmethod
    def make_secure(s):
        return s + "|" + hmac.new(SECRET, s).hexdigest()

    def check_secure_val(self, s):
        val = s.split("|")[0]
        return val if s == self.make_secure(val) else None

    def get(self):
        visit_cookie_str = self.request.cookies.get("visits")
        visits = 0
        if visit_cookie_str:
            cookie_val = self.check_secure_val(visit_cookie_str)
            if cookie_val:
                visits = int(cookie_val)
        visits += 1

        self.response.headers.add_header('Set-Cookie', 'visits=%s' % self.make_secure(str(visits)))
        self.response.headers['Content-Type'] = 'Text/plain'

        self.write("You've been here %d time" % visits)
