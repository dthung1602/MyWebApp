import math
import time
from datetime import datetime
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
        month.update()
        time.sleep(0.2)
        self.redirect("/moneyM1522/{}".format(month.key().id()))


class MoneyMonth(Handler):
    def get(self, month_id):
        month = Month.get_by_id(int(month_id))
        if month is None:
            self.redirect("/moneyM1522/home")
        else:
            self.render_current_month(month)

    def post(self, month_id):
        month = Month.get_by_id(int(month_id))
        if month is None:
            self.redirect("/moneyM1522/home")
        else:
            if self.request.get("action") == "Add":
                self.add_good(month)
            else:
                self.end_month(month)

    def render_current_month(self, month):
        buyers = list(Buyer.get_all_buyers())

        for buyer in buyers:
            buyer.money = buyer.get_money_in_month(month)
            buyer.charge = month.roundup - buyer.money

        self.render("money_current_month.html", month=month, buyers=buyers)

    def add_good(self, month):
        # todo validate info
        good = Good(
            month_id=month.key().id(),
            price=int(self.request.get("price")),
            what=self.request.get("what"),
            buyer=self.request.get("buyer")
        )
        good.put()
        month.update()
        time.sleep(1)
        self.render_current_month(month)

    def end_month(self, old_month):
        # create new month
        new_month = Month(last_month_left=old_month.next_month_left)
        new_month.prev_month = old_month.key().id()
        new_month.put()
        new_month.update()

        # end old month
        old_month.time_end = datetime.now()
        old_month.next_month = new_month.key().id()
        old_month.put()

        time.sleep(1)
        self.render_current_month(old_month)


#############################################################
#                     Database classes                      #
#############################################################

class Buyer(db.Model):
    name = db.StringProperty(required=True)

    @staticmethod
    def get_all_buyers():
        return db.GqlQuery("SELECT * FROM Buyer ORDER BY name ASC")

    def get_money_in_month(self, month):
        goods = db.GqlQuery(
            "SELECT * FROM Good WHERE month_id={} AND buyer='{}' ORDER BY date ASC".format(month.key().id(), self.name))
        return sum(good.price for good in goods)


class Month(db.Model):
    last_month_left = db.IntegerProperty(required=True)
    next_month_left = db.IntegerProperty()

    spend = db.IntegerProperty()
    total_money = db.IntegerProperty()
    average = db.FloatProperty()
    roundup = db.IntegerProperty()

    time_begin = db.DateTimeProperty(auto_now_add=True)
    time_end = db.DateTimeProperty()

    next_month = db.IntegerProperty()
    prev_month = db.IntegerProperty()

    @staticmethod
    def round_up(n):
        return int(math.ceil(n / 10) * 10)

    def update(self):
        buyers = list(Buyer.get_all_buyers())
        self.spend = self.sum()
        self.total_money = self.spend - self.last_month_left
        self.average = self.total_money * 1.0 / len(buyers)
        self.roundup = self.round_up(self.average)
        self.next_month_left = self.roundup * len(buyers) - self.total_money
        self.put()

    def to_string(self):
        new_time = self.time_begin + timedelta(days=4)
        if new_time.month != self.time_begin.month:
            return new_time.month.strftime("%B %Y")
        return self.time_begin.strftime("%B %Y")

    def get_goods(self):
        return db.GqlQuery("SELECT * FROM Good WHERE month_id={} ORDER BY date ASC".format(self.key().id()))

    def sum(self):
        return sum(good.price for good in self.get_goods())


class Good(db.Model):
    month_id = db.IntegerProperty(required=True)
    date = db.DateTimeProperty(auto_now_add=True)
    price = db.IntegerProperty(required=True)
    what = db.StringProperty(required=True)
    buyer = db.StringProperty(required=True)
