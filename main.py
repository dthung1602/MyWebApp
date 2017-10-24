import webapp2
from MyHandlers import *

Handler.handlers = [
    ('/', MainPage.MainPage, False),
    ('/test', Test.Test, True),

    ('/rot13', Rot13.Rot13, True),

    ('/signup', Signup.SignUp, True),
    ('/signin', SignIn.SignIn, True),
    ('/signout', SignOut.SignOut, True),
    ('/welcome', Welcome.Welcome, False),

    ('/ascii_art', ASCIIArt.AsciiArt, True),

    ('/blog', Blog.BlogHomePage, True),
    ('/blog/([0-9]+)', Blog.BlogHandler, False),
    ('/blog/newpost', Blog.NewPostHandler, False),

    ('/moneyM1522/home', MoneyHome.MoneyHome, True),
]

app = webapp2.WSGIApplication(Handler.handlers, debug=True)
