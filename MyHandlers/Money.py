"""
    This function has been moved to project MoneyCalculation
    https://money-calculation-m1522.appspot.com/home
"""
import re
from datetime import datetime
from datetime import timedelta
from google.appengine.ext import db
from math import ceil
from time import sleep

import Handler
from Handler import Handler as Hl


#############################################################
#                    Redirect handler                       #
#############################################################

class RedirectHandler(Hl):
    """Redirect all request to new project"""

    page_title = "Money calculation"

    def get(self, *args, **kwargs):
        self.redirect("https://money-calculation-m1522.appspot.com/home")

    def post(self, *args, **kwargs):
        self.error(405)


#############################################################
#                    Utility functions                      #
#############################################################

def round_up10(n):
    return int(ceil(n / 10.0) * 10)


def round_float(f):
    return "{0:.2f}".format(f)


def format_number(n):
    print(n)
    if isinstance(n, float):
        print("int")
        return "{0:,.2f}".format(n).replace(',', ' ')
    else:
        print("float")
        return "{:,}".format(n).replace(',', ' ')


Handler.jinja_env.globals['round_float'] = round_float
Handler.jinja_env.globals['format_number'] = format_number


#############################################################
#                Request Handler classes                    #
#############################################################

class Home(Hl):
    """Handle home page"""

    page_title = "Monthly money calculation"

    def get(self):
        """Render home page"""
        query = db.GqlQuery("SELECT * FROM Month ORDER BY time_begin DESC")
        months = [m for m in query]
        if len(months) == 0:
            self.render("money_home.html")
        else:
            self.render("money_home.html", months=months)

    def post(self):
        """Create first new month"""
        # check if Month is empty
        query = db.GqlQuery("SELECT * FROM Month ORDER BY time_begin DESC")
        months = [m for m in query]
        if len(months) != 0:
            self.render("money_home.html", error=["New month is created automatically when user ends current month."],
                        months=months)
            return

        # new month
        month = Month.new_month()
        self.redirect("/moneyM1522/{}".format(month.key().id()))


class Monthly(Hl):
    """Handle request for a particular month"""

    def get(self, month_id):
        """Get month info and render html"""
        month = Month.get_by_id(int(month_id))
        if month is None:
            self.error(404)
        else:
            self.render_current_month(month)

    def post(self, month_id):
        """Handle 2 actions: add new Good & end current month"""
        month = Month.get_by_id(int(month_id))
        if month is None:  # invalid month id
            self.error(404)
        else:
            if self.request.get("action") == "Add":
                self.add_good(month)
            else:
                self.end_month(month)

    def render_current_month(self, month, error=[]):
        """Render money_current_month.html"""
        buyers = list(Buyer.get_all_buyers())

        # calculate and put attributes to buyer objects
        usage = {}
        for u in MoneyUsage.get_usage_in_month(month):
            usage[u.buyer_id] = u

        for buyer in buyers:
            u = usage[buyer.key().id()]
            buyer.money = u.money_spend
            buyer.last_month_left = u.last_month_left
            buyer.charge = u.money_to_pay
            buyer.roundup = u.roundup
            buyer.next_month_left = u.next_month_left

        self.render("money_current_month.html", month=month, buyers=buyers, error=error, round_float=round_float,
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
                raise ValueError
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
        sleep(0.5)
        MoneyUsage.update(good)
        month.update()
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
        new_month = Month.new_month(old_month)

        # end old month
        old_month.time_end = datetime.now()
        old_month.next_month = new_month.key().id()
        old_month.put()

        sleep(0.8)
        self.render_current_month(old_month)


#############################################################
#                     Database classes                      #
#############################################################

class Buyer(db.Model):
    name = db.StringProperty(required=True)

    __number_of_buyers__ = None

    @staticmethod
    def get_all_buyers():
        return db.GqlQuery("SELECT * FROM Buyer ORDER BY name ASC")

    @classmethod
    def get_number_of_buyers(cls):
        if not cls.__number_of_buyers__:
            cls.__number_of_buyers__ = cls.all(keys_only=True).count()
        return cls.__number_of_buyers__

    def get_money_in_month(self, month):
        goods = db.GqlQuery(
            "SELECT * FROM Good WHERE month_id={} AND buyer={} ORDER BY date ASC".format(month.key().id(),
                                                                                         self.key().id()))
        return sum(good.price for good in goods)


class Month(db.Model):
    spend = db.IntegerProperty()
    average = db.FloatProperty()

    time_begin = db.DateTimeProperty(auto_now_add=True)
    time_end = db.DateTimeProperty()

    next_month = db.IntegerProperty()
    prev_month = db.IntegerProperty()

    @staticmethod
    def new_month(old_month=None):
        # create new month
        month = Month(spend=0, average=0.0)
        buyers = list(Buyer.get_all_buyers())

        # link new month to old month
        old_month_money_usages = {}
        if old_month is not None:
            month.prev_month = old_month.key().id()
            usages = MoneyUsage.get_usage_in_month(old_month)
            old_month_money_usages = {usage.buyer_id: usage.next_month_left for usage in usages}

        month.put()
        sleep(0.3)

        # create corresponding money usage for each user in this month
        for buyer in buyers:
            bid = buyer.key().id()
            last_month_left = old_month_money_usages.get(bid, 0.0)
            money_usage = MoneyUsage(
                buyer_id=bid,
                month_id=month.key().id(),
                last_month_left=last_month_left,
                next_month_left=last_month_left,
                money_spend=0,
                money_to_pay=-last_month_left,
                roundup=0
            )
            money_usage.put()

        sleep(1)
        return month

    def update(self):
        nob = Buyer.get_number_of_buyers()
        self.spend = self.sum()
        self.average = (self.spend * 1.0 / nob) if nob > 0 else 0.0
        self.put()
        sleep(0.5)

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


class MoneyUsage(db.Model):
    buyer_id = db.IntegerProperty(required=True)
    month_id = db.IntegerProperty(required=True)

    last_month_left = db.FloatProperty(required=True)
    next_month_left = db.FloatProperty(required=True)

    money_spend = db.IntegerProperty(required=True)
    money_to_pay = db.FloatProperty(required=True)
    roundup = db.IntegerProperty(required=True)

    @staticmethod
    def get_usage_in_month(month):
        return db.GqlQuery("SELECT * FROM MoneyUsage WHERE month_id={}".format(month.key().id()))

    @staticmethod
    def update(good):
        avg_price = good.price * 1.0 / Buyer.get_number_of_buyers()
        for usage in db.GqlQuery("SELECT * FROM MoneyUsage WHERE month_id={}".format(good.month_id)):
            usage.money_to_pay += avg_price
            if usage.buyer_id == good.buyer:
                usage.money_spend += good.price
                usage.money_to_pay -= good.price
            usage.roundup = round_up10(usage.money_to_pay)
            usage.next_month_left = usage.roundup - usage.money_to_pay
            usage.put()
        sleep(0.8)
