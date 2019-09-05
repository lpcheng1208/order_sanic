import os
from optparse import OptionParser

from sanic import Sanic, Blueprint
from sanic_motor import BaseModel

from apis import api
from config.settings import logging_config
from extends.aio_redis import rds, rds_1
from extends.aio_mysql import db_sql

from sanic_cors import CORS, cross_origin
from sanic.log import *
import logging
import logging.handlers
import aelog


# logging.basicConfig(filename="access.log")
environ_data = os.environ

app = Sanic('Order', strict_slashes=False, configure_logging=logging_config)

# aelog.init_app(aelog_access_file='log/aelog_access_file.log', aelog_error_file='log/aelog_error_file.log',
#                aelog_console=False)
app.config.update(
    {
        "ACLIENTS_REDIS_HOST": environ_data.get("ACLIENTS_REDIS_HOST", "127.0.0.1"),
        "ACLIENTS_REDIS_PORT": environ_data.get("ACLIENTS_REDIS_PORT", 6380),
        "ACLIENTS_REDIS_DBNAME": environ_data.get("ACLIENTS_REDIS_PORT", 0),
        "ACLIENTS_REDIS_PASSWD": environ_data.get("ACLIENTS_REDIS_PASSWD", ""),
        "ACLIENTS_REDIS_POOL_SIZE": environ_data.get("ACLIENTS_REDIS_POOL_SIZE", 10),

        'ACLIENTS_MYSQL_HOST': environ_data.get("ACLIENTS_MYSQL_HOST", "127.0.0.1"),
        'ACLIENTS_MYSQL_PASSWD': environ_data.get("ACLIENTS_MYSQL_PASSWD", "abcd1234"),
        'ACLIENTS_MYSQL_USERNAME': environ_data.get("ACLIENTS_MYSQL_USERNAME", "root"),
        'ACLIENTS_MYSQL_PORT': environ_data.get("ACLIENTS_MYSQL_PORT", 3306),
        'ACLIENTS_MYSQL_DBNAME': environ_data.get("ACLIENTS_MYSQL_DBNAME", "test"),
        'ACLIENTS_MYSQL_POOL_SIZE': environ_data.get("ACLIENTS_MYSQL_POOL_SIZE", 50),

        'MOTOR_URI': environ_data.get("MOTOR_URI", 'mongodb://test:12345678@localhost:27017/test'),
    }
)
mon_db = BaseModel()
mon_db.init_app(app)
rds.init_app(app)
rds_1.init_app(app)
db_sql.init_app(app)
app.db = db_sql
app.mon_db = mon_db
app.rds = rds
app.rds_1 = rds_1

# cors = CORS(app, resources={r"/apis/*": {"origins": "*"}})

bp_group = Blueprint.group(api, url_prefix='')
app.blueprint(bp_group)

# app.register_listener(setup_mysql, 'before_server_start')
# app.register_listener(setup_redis, 'before_server_start')


# @app.middleware('request')
# async def halt_request(request):
#     return text('I halted the request')
#
#
# @app.middleware('response')
# async def halt_response(request, response):
#     return text('I halted the response')

def initLog(options):
    log_path = os.path.dirname(options.logfile)
    if not os.path.isdir(log_path):
        os.makedirs(log_path)
    logger = logging.getLogger()
    hdlr = logging.handlers.TimedRotatingFileHandler(options.logfile, when='midnight', backupCount=options.backupCount)
    formatter = logging.Formatter("[%(asctime)s]: %(filename)s:%(lineno)d %(levelname)s %(message)s ")
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    if options.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

def main():
    parser = OptionParser(usage="usage: python %prog [options] filename",
                          version="order server v%s" % "1.0")
    parser.add_option("-p", "--port",
                      action="store",
                      type="int",
                      dest="port",
                      default=8686,
                      help="Listen Port")
    parser.add_option("-f", "--logfile",
                      action="store",
                      type="string",
                      dest="logfile",
                      default='./log/run.log',
                      help="LogFile Path and Name. default=./run.log")

    parser.add_option("-n", "--backupCount",
                      action="store",
                      type="int",
                      dest="backupCount",
                      default=10,
                      help="LogFile BackUp Number")
    parser.add_option("-m", "--master",
                      action="store_true",
                      dest="master",
                      default=False,
                      help="master process")
    parser.add_option("-d", "--debug",
                      action="store_true",
                      dest="debug",
                      default=True,
                      help="debug mode")
    (options, args) = parser.parse_args()
    app.run(host='0.0.0.0', port=options.port, debug=False, access_log=False, workers=1, auto_reload=True)

if __name__ == '__main__':
    main()