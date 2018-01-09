import sys
import traceback
from time import sleep

from google.appengine.ext import db

from MyHandlers.Money import Month, Buyer, MoneyUsage, round_up10


def list_month():
    months = db.GqlQuery("SELECT * FROM Month")
    for month in months:
        print month.to_string_short() + " " + month.to_string_long(),
        print "  ID = {}".format(month.key().id())
    print("")


def print_month(month):
    print month.to_string_short()
    print month.to_string_long()
    print "  ID = {}".format(month.key().id())
    print "Spend = %d" % month.spend
    print "Average = %f" % month.average
    print "\n\n"


def print_usage(usage):
    print("NAME: %s" % Buyer.get_by_id(usage.buyer_id).name)
    print("Last month left = %f" % usage.last_month_left)
    print("Next month left = %f" % usage.next_month_left)
    print("Money spend = %d" % usage.money_spend)
    print("Money to pay = %f" % usage.money_to_pay)
    print("Round up = %d" % usage.roundup)
    print("-----------------------------")


def print_good(good):
    print "{} {} {}".format(Buyer.get_by_id(good.buyer).name, good.what, good.price)


def recalculate(month_id):
    """
        Recalculate summarize of a month and its money usages
        Used when delete a Good entity manually
        Compatible with database schema version 2.1
    """
    try:
        # get month
        month = Month.get_by_id(month_id)
        if month is None:
            raise ValueError("Invalid month id")

        # get data
        nob = Buyer.get_number_of_buyers()
        usages = MoneyUsage.get_usage_in_month(month)

        # update money spend in month
        for usage in usages:
            goods = list(db.GqlQuery("SELECT * FROM Good WHERE buyer = {}".format(usage.buyer_id)))
            usage.money_spend = sum(good.price for good in goods)
            usage.put()
        sleep(1.5)

        # recalculate summary of month
        s = sum(usage.money_spend for usage in usages)
        month.spend = s
        month.average = (s * 1.0 / nob) if nob > 0 else 0.0
        month.put()
        sleep(0.25)

        # update money to pay, roundup, next month left
        usage_temps = []
        for usage in usages:
            usage_temps.append(month.average - usage.money_spend - usage.last_month_left)
        for usage in usages:
            temp = usage_temps.pop(0)
            usage.money_to_pay = temp
            usage.roundup = round_up10(temp)
            usage.next_month_left = round_up10(temp) - temp
            usage.put()
        sleep(1.5)

        # print summarize
        print_month(month)
        for usage in usages:
            print_usage(usage)
        print("\nRecalculate done!")
    except Exception:
        print("ERROR!")
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stdout)

