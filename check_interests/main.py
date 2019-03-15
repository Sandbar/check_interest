from flask import Flask
from flask import request
import log_maker
import os
import check_interests as cint

app = Flask(__name__)


@app.route('/', methods=['GET'])
def check_interest():
    try:
        if request.method == 'GET':
            cint.main()
            log_maker.logger.info('OK')
            return "OK"
        else:
            return "it's get request"
    except Exception as e:
        print(str(e))
        log_maker.logger.info(str(e))
        return "except"


app.run('0.0.0.0', os.environ['tm_port'])

