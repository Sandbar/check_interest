
from pymongo import MongoClient
import os


def remove_interests(sid):
    client = MongoClient(os.environ['mongo_url'], maxPoolSize=200)
    db = client.get_database(os.environ['db_name'])
    db.baits.remove({'status': 'available', 'algo': 'random', 'pt.adset_spec.targeting.interests': str(sid)})