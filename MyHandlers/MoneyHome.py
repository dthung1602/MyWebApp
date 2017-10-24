import time

from google.appengine.ext import db

from Handler import Handler


class MoneyHome(Handler):
    def get(self):
        query = db.GqlQuery("SELECT * FROM Month ORDER BY time_begin DESC")
        months = [m.time_begin.strftime("%B %Y") for m in query]
        if len(months) == 0:
            self.render("money_home.html")
        else:
            self.render("money_home.html", months=months)

    def post(self):
        month = Month(last_month_left=0)
        month.put()
        time.sleep(0.2)
        self.redirect("/rot13")  # TODO


class MoneyMonth(Handler):
    def get(self):
        self.render()


#############################################################
#                     Database classes                      #
#############################################################

class Buyer(db.Model):
    name = db.StringProperty(required=True)


class Month(db.Model):
    last_month_left = db.IntegerProperty(required=True)
    time_begin = db.DateProperty(auto_now_add=True)
    time_end = db.DateProperty()


class Good(db.Model):
    month = db.StringProperty(required=True)
    price = db.IntegerProperty(required=True)
    what = db.StringProperty(required=True)
    buyer = db.StringProperty(required=True)
