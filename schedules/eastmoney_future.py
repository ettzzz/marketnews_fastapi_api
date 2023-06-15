
import time
import random

from database.futurenews_operator import futureNewsDatabaseOperator
from scrapper.eastmoney_future import eastmoneyFutureScrapper
from utils.gibber import logger

def eastmoney_future_update(from_date=None):
    source = "eastmoney_future"
    efs = eastmoneyFutureScrapper()
    his_operator = futureNewsDatabaseOperator()
    conn = his_operator.on()

    if from_date is not None:
        stop_timestamp = from_date + " " + "00:00:00"
    else:
        stop_timestamp = his_operator.get_latest_news_timestamp(source=source, conn=conn)

    sortEnd = ""
    fetched = list()
    to_break = False
    while True:
        ef_params = efs.get_params(sortEnd=sortEnd)
        ef_news, sortEnd = efs.get_news(ef_params)
        for n in ef_news:
            if n["timestamp"] > stop_timestamp:
                fetched.append(n)
            else:
                to_break = True
                break

        if len(fetched) > 1000:
            his_operator.insert_news_data(fetched, source, conn)
            fetched.clear()

        if to_break:
            break
        time.sleep(0.5 + random.random())

    if len(fetched) > 0:
        his_operator.insert_news_data(fetched, source, conn)
        
    logger.info(f"from {__file__}: {source} news update done.")
    his_operator.off()
    return

if __name__ == "__main__":
    eastmoney_future_update()
    print("done")