

import requests
from utils.datetime_tools import DATE_TIME_FORMAT
from utils.gibber import logger

class eastmoneyFutureScrapper:
    def __init__(self):
        self.base_url = "https://np-futurelist.eastmoney.com/comm/future/fastNews"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:102.0) Gecko/20100101 Firefox/102.0",
            "Accept": "application/json, text/plain, */*",
            "Host": "np-futurelist.eastmoney.com",
            "Origin": "https://qhweb.eastmoney.com",
            "Referer": "https://qhweb.eastmoney.com/",
            }
        self.timestamp_format = DATE_TIME_FORMAT

    def _data_cleaner(self, news_dict):
        fid = news_dict['newsId']
        content = news_dict['digest'].strip()
        timestamp = news_dict['showTime'] # already DATE_TIME_FORMAT

        return {'fid': fid,
                'source': 'eastmoney_future',
                'content': content,
                'timestamp': timestamp,
                'industry': '',
                'comment': ''}

    def get_params(self, sortEnd="", pageSize=20):
        params = {
        	"biz": "future_724",
        	"client": "future_web",
        	"impt": False,
        	"pageSize": pageSize,
        	"req_trace": "litu37wg-r2c6qqjm",
        	"sortEnd": sortEnd,
        	"version": "1.0.0"
        }
        return params

    def get_news(self, params, retry=0, standard=True):
        if retry > 3:
            logger.error(f"from {__file__}: network error and exceed max retry.")
            return [], ""
        try:
            r = requests.post(
                url=self.base_url,
                json=params,
                headers=self.headers,
                timeout=30)
            if r.status_code == 200:
                content = r.json()
                last_timestamp = content["data"][-1]["sort"]
                if standard:
                    content = [self._data_cleaner(i) for i in content["data"]]
                return content, last_timestamp
            else:
                logger.fatal(f'from {__file__}: Requesting failed! check url \n{r.url}')
                return [], ""
        except:
            return self.get_news(params, retry+1, standard=standard)

if __name__ == "__main__":
    t = eastmoneyFutureScrapper()
    p = t.get_params()
    n, _t = t.get_news(p)