

from flask import Flask
from flask import request
import log_maker
import os
import check_validity_multithread as cvm

app = Flask(__name__)


@app.route('/checkinterest', methods=['GET'])
def check_interest():
    try:
        if request.method == 'GET':
            cvm.find_invalid()
            log_maker.logger.info('OK')
            print('OK')
            return "OK"
    except Exception as e:
        print(str(e))
        log_maker.logger.info(str(e))
        return "except"


app.run('0.0.0.0', os.environ['tm_port'])
