import time

from google.appengine.ext import db

from Handler import Handler


class MoneyHome(Handler):
    def get(self):
        query = db.GqlQuery("SELECT * FROM Month ORDER BY time_begin DESC")
        months = [m.time_begin for m in query]
        if len(months) == 0:
            self.render("money_home.html")
        else:
            self.render("money_home.html", months=months)

    def post(self):
        month = Month(last_month_left=0)
        month.put()
        time.sleep(0.2)
        self.redirect("/moneyM1522/{}".format(month.get_short_key()))


# todo: old month
class MoneyMonth(Handler):
    def get(self, month_short_key):
        for month in db.GqlQuery("SELECT * FROM Month"):
            if month.get_short_key() == month_short_key:
                print "\n>>>>>>>>>>>"
                print [_ for _ in month.get_goods()]
                print "<<<<<<"
                if month.time_end is None:
                    self.render("money_current_month.html", month=month, buyers=Buyer.get_all_buyers())
                else:
                    self.render("money_old_month.html", month=month, buyers=Buyer.get_all_buyers())
                return
        self.redirect("/moneyM1522/home")

    def post(self, month_short_key):
        for month in db.GqlQuery("SELECT * FROM Month"):
            if month.get_short_key() == month_short_key:
                if month.time_end is None:
                    # todo validate info
                    good = Good(
                        month_id=month.key().id(),
                        price=int(self.request.get("price")),
                        what=self.request.get("what"),
                        buyer=self.request.get("buyer")
                    )
                    good.put()
                    time.sleep(0.2)
                    self.render("money_current_month.html", month=month, buyers=Buyer.get_all_buyers())
                else:
                    self.render("money_old_month.html", month=month, buyers=Buyer.get_all_buyers(),
                                error="Content of old months cannot be changed.")
                return
        self.redirect("/moneyM1522/home")


#############################################################
#                     Database classes                      #
#############################################################

class Buyer(db.Model):
    name = db.StringProperty(required=True)

    @staticmethod
    def get_all_buyers():
        return db.GqlQuery("SELECT * FROM Buyer")


class Month(db.Model):
    last_month_left = db.IntegerProperty(required=True)
    time_begin = db.DateProperty(auto_now_add=True)
    time_end = db.DateProperty()

    def get_short_key(self):
        return self.time_begin.strftime("%b%Y")

    def get_goods(self):
        return db.GqlQuery("SELECT * FROM Good WHERE month_id={} ORDER BY date ASC".format(self.key().id()))


class Good(db.Model):
    month_id = db.IntegerProperty(required=True)
    date = db.DateTimeProperty(auto_now_add=True)
    price = db.IntegerProperty(required=True)
    what = db.StringProperty(required=True)
    buyer = db.StringProperty(required=True)
