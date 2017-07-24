from Handler import Handler

class Welcome(Handler):
    def get(self):
        user = self.request.get("user")
        if user:
            self.render("welcome.html", user=user)
