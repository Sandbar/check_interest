import requests
import json
import os
from connect_database import DataManager
from multiprocessing import Queue
import threading
import log_maker


interests_queue = Queue(20000)
items_to_delete_queue = dict()
cnt_progress = 0
lock = threading.Lock()

def check_validity_from_facebook(tp='adinterest', q=None):
    if q:
        res = requests.get('https://graph.facebook.com/v3.1/search?type={0}&q={1}&access_token={2}'.format(tp, q, os.environ['access_token']))
        res = json.loads(res.text)['data']
        return res
    return []


def find_invalid():
    log_maker.logger.info('entry into programmer')
    dm = DataManager()
    interests = dm.get_interests()
    log_maker.logger.info('the size of interests is %d' % (len(interests)))
    for index in range(len(interests)):
        interests_queue.put(interests.iloc[index])
    thread_list = []
    for i in range(int(os.environ['nthread'])):
        thread = threading.Thread(target=query_task,
                                  args=(interests_queue, items_to_delete_queue),
                                  name='facebook-check-validity-' + str(i))
        thread_list.append(thread)
        thread.start()
    for thread in thread_list:
        thread.join()
    for kid, value in items_to_delete_queue.items():
        res = check_validity_from_facebook(q=value)
        if len(res) == 0:
            log_maker.logger.info(str('delete: '+kid+' '+value))
            dm.delete_interest(kid)
    log_maker.logger.info("delete %d interests" % (len(items_to_delete_queue)))


def query_task(interests_queue, items_to_delete_queue):
    global cnt_progress
    while not interests_queue.empty():
        lock.acquire()
        try:
            cnt_progress += 1
        finally:
            lock.release()
        item = interests_queue.get()
        try:
            res = check_validity_from_facebook(q=item['name'])
            if len(res) == 0:
                items_to_delete_queue[item['id']] = item['name']
        except Exception as e:
            log_maker.logger.info(str(item['id']+' '+item['name']+','+str(e)))
            pass


if __name__ == '__main__':
    print(find_invalid())
