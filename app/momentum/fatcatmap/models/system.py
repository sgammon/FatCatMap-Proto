from google.appengine.ext import db


class _SystemProperty_(db.Expando):

    name = db.StringProperty()


class _SysTempData_(db.Expando):

    name = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add=True)
    expiration = db.DateTimeProperty(default=tempExpiration())