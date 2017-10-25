import time
from datetime import timedelta

from google.appengine.ext import db

from Handler import Handler


class MoneyHome(Handler):
    def get(self):
        query = db.GqlQuery("SELECT * FROM Month ORDER BY time_begin DESC")
        months = [m for m in query]
        if len(months) == 0:
            self.render("money_home.html")
        else:
            self.render("money_home.html", months=months)

    def post(self):
        # todo check empty months
        month = Month(last_month_left=0)
        month.put()
        time.sleep(0.2)
        self.redirect("/moneyM1522/{}".format(month.key().id()))


# todo: old month
class MoneyMonth(Handler):
    def get(self, month_id):
        month = Month.get_by_id(int(month_id))
        if month is None:
            self.redirect("/moneyM1522/home")
        else:
            if month.time_end is None:
                self.render("money_current_month.html", month=month, buyers=Buyer.get_all_buyers())
            else:
                self.render("money_old_month.html", month=month, buyers=Buyer.get_all_buyers())

    def post(self, month_id):
        month_id = int(month_id)
        month = Month.get_by_id(month_id)
        if month is None:
            self.redirect("/moneyM1522/home")
        else:
            if month.time_end is None:
                # todo validate info
                good = Good(
                    month_id=month_id,
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


#############################################################
#                     Database classes                      #
#############################################################

class Buyer(db.Model):
    name = db.StringProperty(required=True)

    @staticmethod
    def get_all_buyers():
        return db.GqlQuery("SELECT * FROM Buyer ORDER BY name ASC")


class Month(db.Model):
    last_month_left = db.IntegerProperty(required=True)
    time_begin = db.DateProperty(auto_now_add=True)
    time_end = db.DateProperty()

    def to_string(self):
        new_time = self.time_begin + timedelta(days=4)
        if new_time.month != self.time_begin.month:
            return new_time.month.strftime("%B %Y")
        return self.time_begin.strftime("%B %Y")

    def get_goods(self):
        return db.GqlQuery("SELECT * FROM Good WHERE month_id={} ORDER BY date ASC".format(self.key().id()))


class Good(db.Model):
    month_id = db.IntegerProperty(required=True)
    date = db.DateTimeProperty(auto_now_add=True)
    price = db.IntegerProperty(required=True)
    what = db.StringProperty(required=True)
    buyer = db.StringProperty(required=True)
