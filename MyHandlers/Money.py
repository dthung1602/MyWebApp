import math
import re
import time
from datetime import datetime
from datetime import timedelta

from google.appengine.ext import db

from Handler import Handler


#############################################################
#                Request Handler classes                    #
#############################################################

class Home(Handler):
    """Handle home page"""

    def get(self):
        """Render home page"""
        query = db.GqlQuery("SELECT * FROM Month ORDER BY time_begin DESC")
        months = [m for m in query]
        if len(months) == 0:
            self.render("money_home.html", __page_title__="Monthly money calculation")
        else:
            self.render("money_home.html", months=months, __page_title__="Monthly money calculation")

    def post(self):
        """Create first new month"""
        # check if Month is empty
        query = db.GqlQuery("SELECT * FROM Month ORDER BY time_begin DESC")
        months = [m for m in query]
        if len(months) != 0:
            self.render("money_home.html", error=["New month is created automatically when user ends current month."],
                        __page_title__="Monthly money calculation", months=months)
            return

        # new month
        month = Month(last_month_left=0, spend=0, total_money=0, average=0.0, roundup=0, next_month_left=0)
        month.put()
        time.sleep(0.6)
        self.redirect("/moneyM1522/{}".format(month.key().id()))


class Monthly(Handler):
    """Handle request for a particular month"""

    def get(self, month_id):
        """Get month info and render html"""
        month = Month.get_by_id(int(month_id))
        if month is None:
            self.redirect("/moneyM1522/home")
        else:
            self.render_current_month(month)

    def post(self, month_id):
        """Handle 2 actions: add new Good & end current month"""
        month = Month.get_by_id(int(month_id))
        if month is None:  # invalid month id
            self.redirect("/moneyM1522/home")
        else:
            if self.request.get("action") == "Add":
                self.add_good(month)
            else:
                self.end_month(month)

    def render_current_month(self, month, error=[]):
        """Render money_current_month.html"""
        buyers = list(Buyer.get_all_buyers())

        # calculate and put attributes to buyer objects
        for buyer in buyers:
            buyer.money = buyer.get_money_in_month(month)
            buyer.charge = month.roundup - buyer.money

        self.render("money_current_month.html", month=month, buyers=buyers, error=error,
                    __page_title__=month.to_string_short())

    def add_good(self, month):
        """add a good to database"""
        # get info
        month_id = month.key().id()
        price = self.request.get("price")
        what = self.request.get("what")
        buyer = self.request.get("buyer")

        # validate
        error = []
        # check for empty fields
        if None in [price, what, buyer]:
            error.append("Please fill all information")
        # check if buyer exists
        try:
            buyer = int(buyer)
            if Buyer.get_by_id(buyer) is None:
                raise
        except ValueError:
            error.append("Invalid buyer")
        # evaluate price
        try:
            if not re.match("^[0-9 \-+*/()]+$", price):
                raise SyntaxError
            price = eval(price)
            if price <= 0 or not isinstance(price, int):
                raise ValueError
        except (SyntaxError, ZeroDivisionError):
            error.append("Invalid arithmetic expression in field price")
        except ValueError:
            error.append("Price must be a positive integer")

        if len(error) > 0:
            self.render_current_month(month, error)
            return

        # put to database
        good = Good(month_id=month_id, price=price, what=what, buyer=buyer)
        good.put()
        time.sleep(0.5)
        month.update()
        time.sleep(0.5)
        self.render_current_month(month)

    def end_month(self, old_month):
        """
            add time_end to old month, making its data can not be change;
            create a new month
        """
        # check if old_month has already ended
        if old_month.time_end is not None:
            self.render_current_month(old_month, ["This month has already ended."])
            return

        # create new month
        new_month = Month(last_month_left=old_month.next_month_left)
        new_month.prev_month = old_month.key().id()
        new_month.put()
        new_month.update()

        # end old month
        old_month.time_end = datetime.now()
        old_month.next_month = new_month.key().id()
        old_month.put()

        time.sleep(0.8)
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
            "SELECT * FROM Good WHERE month_id={} AND buyer={} ORDER BY date ASC".format(month.key().id(),
                                                                                         self.key().id()))
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
        self.average = (self.total_money * 1.0 / len(buyers)) if len(buyers) > 0 else 0.0
        self.roundup = self.round_up(self.average)
        self.next_month_left = self.roundup * len(buyers) - self.total_money
        self.put()

    def to_string_short(self):
        new_time = self.time_begin + timedelta(days=4)
        if new_time.month != self.time_begin.month:
            return new_time.month.strftime("%B %Y")
        return self.time_begin.strftime("%B %Y")

    def to_string_long(self):
        return self.time_begin.strftime("%d/%m/%y") + " - " + \
               (self.time_end.strftime("%d/%m/%y") if self.time_end is not None else "now")

    def get_goods(self):
        goods = []
        for good in db.GqlQuery("SELECT * FROM Good WHERE month_id={} ORDER BY date ASC".format(self.key().id())):
            good.buyer_name = Buyer.get_by_id(int(good.buyer)).name
            goods.append(good)
        return goods

    def sum(self):
        return sum(good.price for good in self.get_goods())


class Good(db.Model):
    month_id = db.IntegerProperty(required=True)
    date = db.DateTimeProperty(auto_now_add=True)
    price = db.IntegerProperty(required=True)
    what = db.StringProperty(required=True)
    buyer = db.IntegerProperty(required=True)
