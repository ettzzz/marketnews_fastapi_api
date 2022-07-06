# -*- coding: utf-8 -*-

import requests
import traceback

from utils.datetime_tools import reverse_timestamper, timestamper


class yuncaijingScrapper:
    def __init__(self):
        self.base_url = (
            "https://www.yuncaijing.com/news/get_realtime_news/yapi/ajax.html"
        )
        self.timestamp_format = int

    def _get_code(self, news_dict):
        if not news_dict["thm_related"] and not news_dict["stktags"]:
            return ""

        codes = []
        if len(news_dict["thm_related"]) > 0:
            for thm in news_dict["thm_related"]:
                if "stock" in thm and type(thm["stock"]) is list:
                    for thm_list in thm["stock"]:
                        codes.append(thm_list["code"])

        if len(news_dict["stktags"]) > 0:
            for j in news_dict["stktags"]:
                codes.append(j["code"])

        return ",".join(codes)

    def _data_cleaner(self, news_dict):
        fid = int(news_dict["id"])
        content = news_dict["title"].strip() + "," + news_dict["description"].strip()
        # timestamp = reverse_timestamper(news_dict['inputtime']) # 10digit to DATE_TIME_FORMAT
        timestamp = self.timestamp_format(
            news_dict["inputtime"]
        )  # thats a fucking mistake
        # timestamp = news_dict['inputtime']
        tag = news_dict["thmtags"].replace(" ", ",")
        code = self._get_code(news_dict)

        return {
            "fid": fid,
            "source": "ycj",
            "content": content,
            "timestamp": timestamp,
            "tag": tag,
            "code": code,
            "industry": "",
            "info": "",
            "comment": "",
        }

    def get_params(self, page, date):
        params = {"page": page, "date": date}  # 2020-08-26
        return params

    def get_news(self, params, standard=True):
        date = params["date"]
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:79.0) Gecko/20100101 Firefox/79.0",
            "Referer": "https://www.yuncaijing.com/insider/list_{}.html".format(date),
            "Host": "www.yuncaijing.com",
            "Origin": "https://www.yuncaijing.com",
            "Cookie": "ycj_wafsid=wafsid_fb0db6857bc227a8ca1aa0a1bbd8c7e5; ycj_uuid=96d6792f5fb5aa66a701bb929af84d63; ycj_from_url=aHR0cHM6Ly9kdWNrZHVja2dvLmNvbS8%3D; ycj_locate=aHR0cHM6Ly93d3cueXVuY2FpamluZy5jb20v; Qs_lvt_168612=1598163066; Qs_pv_168612=3418167207889237500; Hm_lvt_b68ec780c488edc31b70f5dadf4e94f8=1598163069; PHPSESSID=4r7bm8qmcc7nm7gf0vt4borpl4; YUNSESSID=nleq71t123s2p8m6hjmqmg5c01",
        }
        try:
            r = requests.post(url=self.base_url, data=params, headers=headers)
            if r.status_code == 200:
                if r.json()["error_code"] == "0":
                    content = r.json()["data"]
                    if standard:
                        content = [self._data_cleaner(i) for i in content]
                    return content
                else:
                    return []  # page more than capacity
            else:
                print(
                    "from yuncaijingScrapper: Requesting failed! check url \n{}".format(
                        r.url
                    )
                )
                return []
        except:
            e = traceback.print_exc()
            print(
                "from yuncaijingScrapper: Normalizing data error with following exception:\
                  \n {}\
                  \n".format(
                    e
                )
            )
            return []

    def get_filtered_news(self, standard_news_list):
        filtered_news_list = []
        for sn in standard_news_list:
            if sn["code"]:
                filtered_news_list.append(sn)

        return filtered_news_list


if __name__ == "__main__":
    import pandas as pd
    import time
    import random
    from database.news_operator import newsDatabaseOperator
    from utils.datetime_tools import (
        date_range_generator,
        get_today_date,
        get_delta_date,
    )

    # from config.static_vars import DAY_ZERO
    source = "ycj"
    today = get_today_date()
    yesterday = get_delta_date(today, -1)
    his_operator = newsDatabaseOperator()

    news_fields = list(his_operator.news_fields["daily_news"].keys())
    max_id = his_operator.get_latest_news_id(source)
    max_date = his_operator.get_latest_news_date(source)

    ys = yuncaijingScrapper()
    dates = date_range_generator(max_date, yesterday)  # at least yesterday is gone

    for date in dates:
        print("yuncaijing getting news for", date)
        page = 1
        news = []
        while True:
            ycj_params = ys.get_params(page, date)
            ycj_news = ys.get_news(ycj_params)
            if not ycj_news:
                break
            news += ycj_news
            page += 1
            time.sleep(random.random() + random.randint(1, 2))

        if len(news) == 0:
            print("date len news is 0", date)
            continue

        df = pd.DataFrame(news[::-1])  # reverse sequence for yuncaijing
        df = df[(df["fid"] > max_id)]
        fetched = df[news_fields].to_numpy()
        year = date[:4]
        his_operator.insert_news_data(fetched, year, source)
