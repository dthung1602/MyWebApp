import webapp2

from MyHandlers import *

Handler.handlers = [
    ('/', MainPage.MainPage),
    ('/test', Test.Test),

    ('/rot13', Rot13.Rot13),

    ('/signup', Signup.SignUp),
    ('/signin', SignIn.SignIn),
    ('/signout', SignOut.SignOut),
    ('/welcome', Welcome.Welcome),

    ('/ascii_art', ASCIIArt.AsciiArt),

    ('/blog', Blog.BlogHomePage),
    ('/blog/([0-9]+)', Blog.BlogHandler),
    ('/blog/newpost', Blog.NewPostHandler),

    ('/moneyM1522', Money.RedirectHandler),
    ('/moneyM1522/(.*)', Money.RedirectHandler),

    ('/enigma', Enigma.EnigmaRequestHandler),

    # ---- do not add path under this line --------
    ('/(.*)', ErrorHandler.ErrorHandler, None)
]

app = webapp2.WSGIApplication(Handler.handlers, debug=True)
