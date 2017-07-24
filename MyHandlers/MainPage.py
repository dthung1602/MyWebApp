import Handler


class MainPage(Handler.Handler):
    def filter(self, handlers):
        result = []
        for handler in handlers:
            if handler[2]:
                result.append(handler)
        return result

    def get(self):
        h = self.filter(Handler.handlers)
        self.render("index.html", handlers=h)
