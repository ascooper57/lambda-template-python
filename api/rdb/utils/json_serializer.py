import decimal
from datetime import datetime, date
import bson
from uuid import UUID


# noinspection PyPep8Naming
def json_serialize(obj):
    if not len(obj):
        return
    # noinspection PyPep8
    l = [obj] if not isinstance(obj, list) else obj
    for o in l:
        if isinstance(o, str):
            continue
        if isinstance(o, list) and len(o):
            for v in o:
                json_serialize(v)
        else:
            if isinstance(o, list):
                for k, v in enumerate(o):
                    if isinstance(v, dict):
                        json_serialize(v)
                    else:
                        if isinstance(v, datetime):
                            o[k] = "{:%Y-%m-%d %H:%M:%S}".format(v)
                        elif isinstance(v, date):
                            o[k] = "{:%Y-%m-%d}".format(v)
                        elif isinstance(v, decimal.Decimal):
                            o[k] = float(v)
                        elif isinstance(v, UUID):
                            # if the obj is uuid, we simply return the value of uuid
                            o[k] = uuid2string(v)
                        elif isinstance(o[k], bson.ObjectId):
                            o[k] = str(v)
            else:
                for k, v in o.items():
                    if isinstance(v, dict):
                        json_serialize(v)
                    else:
                        if isinstance(v, datetime):
                            o[k] = "{:%Y-%m-%d %H:%M:%S}".format(v)
                        elif isinstance(v, date):
                            o[k] = "{:%Y-%m-%d}".format(v)
                        elif isinstance(v, decimal.Decimal):
                            o[k] = float(v)
                        elif isinstance(v, UUID):
                            # if the obj is uuid, we simply return the value of uuid
                            o[k] = uuid2string(v)
                        elif isinstance(o[k], bson.ObjectId):
                            o[k] = str(v)


# http://www.chanduthedev.com/2014/05/how-to-convert-uuid-to-string-in-python.html
def uuid2string(uid):
    uid_str = uid.urn
    return uid_str[9:]
