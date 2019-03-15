
import requests
import json
import os
from mysql import DataManager
import time
import log_maker
import mongo


def check_one_name_validate(infos, sign=True):
    parames = {
        'type': 'adinterest',
        'q': infos['name'],
        'access_token': os.environ['access_token']
    }
    res = requests.get('https://graph.facebook.com/v3.1/search', params=parames)
    res_json = json.loads(res.text)
    if len(res_json) > 0 and 'data' in res_json:
        for result in res_json['data']:
            if str(infos['id']) == result['id']:
                return True
    if sign and 'type' in infos and len(infos['type']) > 0:
        infos['name'] = infos['name']+', '+infos['type']
        return check_one_name_validate(infos, False)
    return False


def check_all_names_validate():
    dm = DataManager()
    interests = dm.get_interests()
    log_maker.logger.info('get %s interests' % (str(len(interests))))
    interests['name'] = [xx.replace('"', '\"').replace("'", "\'") for xx in interests['name']]
    delete_ids = []
    index = 0
    lens = len(interests)
    while True:
        tindex, index = index, index+1000
        if tindex >= lens:
            break
        stmp = '["'+'","'.join(interests['name'][tindex:index])+'"]'
        params = {
            'type': 'adinterestvalid',
            'interest_list': stmp,
            'access_token': os.environ['access_token']
        }
        res = requests.get('https://graph.facebook.com/v3.1/search', params=params)
        res_json = json.loads(res.text)
        if 'data' in res_json:
            for data in res_json['data']:
                if 'id' not in data or ('valid' in data and not data['valid']):
                    try:
                        infos = dm.select_by_name(data['name'])
                        if not check_one_name_validate(infos):
                            log_maker.logger.info('%s(%s) will be deleted' % (infos['name'], infos['id']))
                            delete_ids.append(infos['id'])
                    except Exception as ex:
                        log_maker.logger.info('%s except,%s' % (data['name'], str(ex)))
                        print(str(ex), data['name'])
                        pass
    log_maker.logger.info('it has %d interests to delete.' % (len(delete_ids)))
    for ids in delete_ids:
        try:
            dm.delete_interest(ids)
            mongo.remove_interests(ids)
            log_maker.logger.info('%s is deleted' % (str(ids)))
        except Exception as ex:
            log_maker.logger.info('deleting %s is failure, %s' % (str(ids), str(ex)))


def main():
    try:
        log_maker.logger.info('entry into main function')
        t1 = time.time()
        check_all_names_validate()
        print(time.time()-t1)
        log_maker.logger.info('It cost %s seconds...' % (str(round(time.time()-t1, 3))))
        return 'OK'
    except Exception as ex:
        log_maker.logger.info('except, %s' % (str(ex)))
        return 'Failure'


if __name__ == '__main__':
    main()
