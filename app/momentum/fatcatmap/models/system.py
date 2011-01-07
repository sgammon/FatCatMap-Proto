import datetime
from google.appengine.ext import db

from ProvidenceClarity.data.core.polymodel import PolyPro


def tempExpiration(timedelta=None, date_time=None):

    if timedelta is None and date_time is None:
        return datetime.datetime.now()+datetime.timedelta(days=6)

    elif timedelta is not None:
        return datetime.datetime.now()+timedelta

    elif datetime is not None:
        return date_time



class _SystemProperty_(db.Expando):

    name = db.StringProperty()


class _SysTempData_(db.Expando):

    name = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add=True)
    expiration = db.DateTimeProperty(default=tempExpiration())

    def setExpiration(self, datetime_object=None, **kwargs):

        if datetime_object is None:
            if isinstance(datetime_object, datetime.timedelta):
                self.expiration = tempExpiration(timedelta=datetime_obj)
            elif isinstance(datetime_object, datetime.datetime):
                self.expiration = tempExpiration(datetime=datetime_obj)

        else:
            self.expiration = tempExpiration(timedelta=datetime.timedelta(**kwargs))


class _ConfigGroup_(PolyPro):
    pass


class _ConfigParam_(db.Expando):

    name = db.StringProperty()
    group = db.ReferenceProperty(_ConfigGroup_, collection_name='params')
    ## 'value' set at runtime


class _Counter_(PolyPro):
    value = db.IntegerProperty()