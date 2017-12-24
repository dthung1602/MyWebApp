import Handler


class MainPage(Handler.Handler):
    page_title = "Main Page"

    @staticmethod
    def filter(handlers):
        result = []
        for handler in handlers:
            name = handler[1].__dict__.get("page_title", None)
            if name:
                result.append((handler[0], name))
        return result

    def get(self):
        h = self.filter(Handler.handlers)
        self.render("index.html", handlers=h)
