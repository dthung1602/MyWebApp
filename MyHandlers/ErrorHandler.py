import Handler


class ErrorHandler(Handler.Handler):
    page_title = "Error"

    def get(self, *args, **kwargs):
        self.error(404)

    def pos(self, *args, **kwargs):
        self.error(404)

    def head(self, *args, **kwargs):
        self.error(404)
