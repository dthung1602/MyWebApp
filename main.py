import webapp2

from MyHandlers import *

Handler.handlers = [
    ('/', MainPage.MainPage, None),
    ('/test', Test.Test, "Test cookie"),

    ('/rot13', Rot13.Rot13, "Rot 13"),

    ('/signup', Signup.SignUp, "Sign up"),
    ('/signin', SignIn.SignIn, "Sign in"),
    ('/signout', SignOut.SignOut, "Sign out"),
    ('/welcome', Welcome.Welcome, None),

    ('/ascii_art', ASCIIArt.AsciiArt, "ASCII art"),

    ('/blog', Blog.BlogHomePage, "Blog home"),
    ('/blog/([0-9]+)', Blog.BlogHandler, False),
    ('/blog/newpost', Blog.NewPostHandler, False),

    ('/moneyM1522/', Money.Home, None),
    ('/moneyM1522/home', Money.Home, "Money M15.22"),
    ('/moneyM1522/([0-9]+)', Money.Monthly, None),

    ('/enigma', Enigma.EnigmaRequestHandler, "Enigma Simulator"),

    # do not add path under this line
    ('/(.*)', ErrorHandler.ErrorHandler, None)
]

app = webapp2.WSGIApplication(Handler.handlers, debug=True)
