


from database.base_mongo import BaseMongoOperator

from config.static_vars import DAY_ZERO, MONGO_URI, DB_NAME


class futureNewsDatabaseOperator(BaseMongoOperator):
    def __init__(self, mongo_uri=MONGO_URI, db_name=DB_NAME):
        super().__init__(mongo_uri, db_name)
        self.chunk_size = 400

    def get_latest_news_timestamp(self, source, key="_id", conn=None):
        if conn is None:
            conn = self.on()
        table_name = source
        if not self.has_table(table_name):
            return DAY_ZERO + " " + "00:00:00"
        else:
            col = conn[table_name]
            res = col.find_one(sort=[(key, -1)])
            if res is None:  ## when collection is empty:
                return DAY_ZERO + " " + "00:00:00"
            else:
                return res["timestamp"]

    def insert_news_data(self, fetched, source, conn):
        if not fetched:
            return
        table_name = source
        col = conn[table_name]
        col.insert_many(fetched)
        return
