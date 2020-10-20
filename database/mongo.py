import pymongo
import json

class GaugeDB():
    def __init__(self):
        print("DataBase communication initialization")
        self.client = self.make_client()
        self.Gauge = self.client.Gauge


    def make_client(self):
        """Utility funciton to load MongoClient"""
        with open('database/mongo-credentials.json', 'r') as f:
            creds = json.load(f)
        self.client = pymongo.MongoClient(creds.get('conn-string'))
        return self.client


    def insert_gauge(self, dict):
        self.Gauge.gauge.insert_one(dict)

    def get_latest_gauge(self):
        return self.Gauge.gauge.find_one(sort=[('_id', pymongo.DESCENDING)])
    
    def get_gauge(self):
        return self.Gauge.gauge.find()

if __name__ == "__main__":
    mongo_client = GaugeDB()
    mongo_client.insert_gauge({"name": "John", "address": "Highway 38"})
    print(mongo_client.get_gauge())
    print(mongo_client.get_latest_gauge())
