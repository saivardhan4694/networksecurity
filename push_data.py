import os
import sys
import json
from dotenv import load_dotenv
from pymongo import MongoClient
import certifi
import pandas as pd
import numpy as np
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

load_dotenv()
MONGO_DB_URL = os.getenv("MONGO_DB_URL")
ca = certifi.where()

class NetworkDataExtract():
    def __init__(self) -> None:
        try:
            pass
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def csv_to_json_converter(self, file_path):
        try:
            data = pd.read_csv(file_path)
            data.reset_index(drop = True, inplace= True)
            records = list(json.loads(data.T.to_json()).values())
            return records
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def insert_data_mongodb(self, records, database, collection):
        try:
            self.database = database
            self.collection = collection
            self.records = records
            self.mongo_client = MongoClient(MONGO_DB_URL)
            self.database = self.mongo_client[self.database]
            self.collection = self.database[self.collection]
            self.collection.insert_many(self.records)
            return(len(self.records))
        except Exception as e:
            raise NetworkSecurityException(e, sys)

if __name__ == "__main__":
    FILE_PATH = r"D:\repositories\NetworkSecurity\Network_Data\phisingData.csv"
    DATABASE = "vardhanDB"
    collection = "NetworkData"
    networkobj = NetworkDataExtract()
    records = networkobj.csv_to_json_converter(file_path=FILE_PATH)
    print(records[1:6])
    no_of_records = networkobj.insert_data_mongodb(records, DATABASE, collection)
    print(no_of_records)

