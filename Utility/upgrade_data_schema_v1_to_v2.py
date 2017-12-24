import sys
import traceback

from MyHandlers.Money import *


def upgrade():
    """Update data schema from version 1.1 to version 2.0"""

    try:
        bids = [bid.key().id() for bid in Buyer.get_all_buyers()]
        nob = len(bids)
        months = db.GqlQuery("SELECT * FROM Month ORDER BY time_begin ASC")

        # create corresponding money usage for each user in this month
        for i in xrange(len(list(months))):
            month = months[i]
            mid = month.key().id()
            avg_last_month_left = months[i - 1].next_month_left * 1.0 / nob if i > 0 else 0.0
            avg_next_month_left = month.next_month_left * 1.0 / nob

            # recalculate properties of month
            month.average = month.spend * 1.0 / nob

            # create money usage
            for bid in bids:
                goods = db.GqlQuery("SELECT * FROM Good WHERE month_id={} AND buyer={}".format(mid, bid))
                money_spend = sum(good.price for good in goods)
                money_to_pay = month.average - avg_last_month_left - money_spend

                money_usage = MoneyUsage(
                    buyer_id=bid,
                    month_id=mid,
                    last_month_left=avg_last_month_left,
                    next_month_left=avg_next_month_left,
                    money_spend=money_spend,
                    money_to_pay=money_to_pay,
                    roundup=int(money_to_pay + avg_next_month_left)
                )
                money_usage.put()

            month.put()
            time.sleep(1.5)
        print("UPDATED!")
    except Exception:
        print("ERROR!")
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
