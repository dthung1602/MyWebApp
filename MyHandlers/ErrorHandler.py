import Handler


class ErrorHandler(Handler.Handler):
    def get(self, *args, **kwargs):
        self.error(404)

    def pos(self, *args, **kwargs):
        self.error(404)

    def head(self, *args, **kwargs):
        self.error(404)
