# -*- coding: utf-8 -*-

import requests
import re

from utils.datetime_tools import timestamper, DATE_TIME_FORMAT
from utils.gibber import logger


class sinaScrapper():
    def __init__(self):
        self.base_url = 'http://zhibo.sina.com.cn/api/zhibo/feed'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:79.0) Gecko/20100101 Firefox/79.0',
            'Referer': 'http://finance.sina.com.cn/7x24/',
            'Host': 'zhibo.sina.com.cn'
        }
        self.timestamp_format = DATE_TIME_FORMAT
        self.callback = 'jQuery0'

    def _data_cleaner(self, news_dict):
        fid = news_dict['id']
        content = news_dict['rich_text'].strip()
        timestamp = str(timestamper(news_dict['create_time'], self.timestamp_format))
        # timestamp = news_dict['create_time']
        tag = ','.join(list(map(lambda x: x['name'], news_dict['tag'])))

        try:
            ext = eval(news_dict['ext'])
            code = ','.join(list(map(lambda x: x['symbol'], ext['stocks'])))
        except Exception as e:
            logger.error('sina code extracting error', e)
            code = ''

        return {'fid': fid,
                'source': 'sina',
                'content': content,
                'timestamp': timestamp,
                # 'date': timestamp.split(' ')[0],
                # 'time': timestamp.split(' ')[1],
                'tag': tag,
                'code': code,
                'industry': '',
                'info': '',
                'comment': ''
                }

    def get_params(self, _id=114514, _type=1, page=1, page_size=100):
        # _type = 0: # get latest 100 news;
        # _type = 1: # get specific news with designated ids
        params = {
            'callback': self.callback,
            'page': page,
            'page_size': page_size,
            'zhibo_id': 152,
            'tag_id': 0,
            'dire': 'f',
            'dpc': 1,
            'pagesize': 20,
            'id': _id,
            'type': _type

        }
        '''
        tag id mapping
        {'1': '宏观', '2': '行业', '3': '公司', '4': '数据', '5': '市场',
         '6': '观点', '7': '央行', '8': '其他', '9': '焦点', '10': 'A股',
         '102': '国际', '110': '疫情',
         }
        '''
        return params

    def get_news(self, params, standard=True):
        '''
        params = {
            'callback': callback,
            'page': 1,
            'page_size': 100,
            'zhibo_id': 152,
            'tag_id': 0,
            'dire': 'f',
            'dpc': 1,
            'pagesize': 20,
            'id': 203152,
            'type': 1, # 1 historical, 0 latest
        }
        return a dictionary contains page_info, max_id, min_id and news list
        '''
        try:
            r = requests.get(
                url=self.base_url,
                params=params,
                headers=self.headers
            )
            if r.status_code == 200:
                text = re.findall(self.callback + r'\((.*)\);}catch', r.text)[0]
                text = text.replace('true', 'True').replace('false', 'False')
                content = eval(text)['result']['data']['feed']
                if standard:
                    cleaned_list = [self._data_cleaner(i) for i in content['list']]
                    content['list'] = cleaned_list
                return content
            else:
                logger.error('from sinaScrapper: Requesting failed! check url \n{}'.format(r.url))
                return {}
        except Exception as e:
            logger.error('from sinaScrapper: Normalizing data error with folling exception:\
                  \n {}\
                  \n'.format(e))
            return {}

    def get_filtered_news(self, standard_news_list):
        filtered_news_list = []
        for sn in standard_news_list:
            if len(re.findall(r's[h,z]\d{6}', sn['code'])) > 0:
                filtered_news_list.append(sn)

        return filtered_news_list


if __name__ == "__main__":
    import pandas as pd
    import time
    import random
    from database.news_operator import newsDatabaseOperator
    from utils.datetime_tools import reverse_timestamper

    source = 'sina'
    his_operator = newsDatabaseOperator()
    news_fields = list(his_operator.news_fields['daily_news'].keys())
    min_id = his_operator.get_zero_news_id(source=source)
    # min_id = his_operator.get_latest_news_id(source=source)
    
    ss = sinaScrapper()
    init_params = ss.get_params(_type=0)
    news = ss.get_news(init_params)

    while news['max_id'] > min_id:
        df = pd.DataFrame(news['list'][::-1])  # reverse sequence for sina
        df = df[(df['fid'] > min_id)]

        df['year'] = df['timestamp'].apply(lambda row: reverse_timestamper(row)[:4])
        years = df['year'].value_counts()
        print(years)
        for year, _count in df['year'].value_counts().items():
            fetched = df[news_fields][(df['year'] == year)].to_numpy()
            his_operator.insert_news_data(fetched, year, source)

        params = ss.get_params(_id=news['min_id'] - 1, _type=1)
        news = ss.get_news(params)
        if len(news) == 0:
            news = ss.get_news(params)  # dumb way to re request
        time.sleep(random.random() + random.randint(1, 2))
