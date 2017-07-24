import webapp2
import MyHandlers
from MyHandlers import ASCIIArt, MainPage, Rot13, Signup, Welcome, Blog

MyHandlers.Handler.handlers = [    
    ('/', MainPage.MainPage, False),  

    ('/rot13', Rot13.Rot13, True),    
        
    ('/signup', Signup.SignUp, True),    
    ('/welcome', Welcome.Welcome, False),

    ('/ascii_art', ASCIIArt.AsciiArt, True),

    ('/blog', Blog.BlogHomePage, True),
    ('/blog/([0-9]+)', Blog.BlogHandler, False),
    ('/blog/newpost', Blog.NewPostHandler, False),
]

app = webapp2.WSGIApplication(MyHandlers.Handler.handlers, debug=True)
