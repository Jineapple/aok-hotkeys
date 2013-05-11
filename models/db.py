import logging as log

if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB
    db = DAL('sqlite://storage.sqlite',pool_size=1,check_reserved=['all'])
else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore', lazy_tables=True)
    ## store sessions and tickets there
    session.connect(request, response, db=db)
    ## or store session in Memcache, Redis, etc.
    #from gluon.contrib.memdb import MEMDB
    #from google.appengine.api.memcache import Client
    #session.connect(request, response, db = MEMDB(Client()))

response.generic_patterns = ['*'] if request.is_local else []
import pickle
from gluon.dal import SQLCustomType
pickled = SQLCustomType(
    type = 'text',
    native = 'text',
    encoder = (lambda x: pickle.dumps(x)),
    decoder = (lambda x: pickle.loads(x))
)
db.define_table('presets', Field('version', 'string', length=3), Field('name', 'string', length=32), Field('assign', pickled), Field('usage', 'integer', default=0))

def arg_cache(cache_key = lambda x: x, time_expire=None):
    def decorator(method):
        def wrap(*args):
            key = cache_key(*args)
            def log_wrap(*args):
                log.info('Caching key {:s}'.format(key)) 
                return method(*args)
            return cache.ram(key, lambda: log_wrap(*args), time_expire=time_expire)
        return wrap
    return decorator
