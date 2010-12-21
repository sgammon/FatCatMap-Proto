##############################################################################
#
# Copyright 2009 Lovely Systems AG
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
##############################################################################

import logging
import pickle

from google.appengine.api import datastore_errors
from google.appengine.ext import db


_log = logging.getLogger(__name__)


class SizedListProperty(db.ListProperty):

    def __init__(self, type, length=None, **kwargs):
        self.length = length
        return super(SizedListProperty, self).__init__(type, **kwargs)

    def validate(self, value):
        value = super(SizedListProperty, self).validate(value)
        if value and self.length is not None and self.length != len(value):
            raise db.BadValueError('Wrong length need %r got %r' % (
                self.length, len(value)))
        return value

class TypedListProperty(SizedListProperty):

    """a property that replaces object with keys and checks the kind
    of objects"""

    def __init__(self, kind, length=None, **kwargs):
        self.length = length
        if not isinstance(kind, basestring):
            if not issubclass(kind, db.Model):
                raise ValueError, "Kind needs to be a subclass of db.Model"
            kind = kind.kind()
        self.item_kind = kind
        return super(TypedListProperty, self).__init__(db.Key,
                                                       length=length, **kwargs)

    def validate(self, value):
        for i, v in enumerate(value):
            if v:
                if isinstance(v, basestring):
                    v = db.Key(v)
                elif isinstance(v, db.Model):
                    v = v.key()
                if v.kind() != self.item_kind:
                    raise db.BadValueError('Wrong kind %r' % v.kind())
            value[i] = v
        return super(TypedListProperty, self).validate(value)


class IStringProperty(db.StringProperty):

    """a property that matches case insensitive on prefix searches"""

    HIGHEST_UNICODE = u'\xEF\xBF\xBD'

    # this is smaller than the highest unicode
    SEPERATOR = u'\xEF\xBF\xBC'

    def validate(self, v):
        v = super(IStringProperty, self).validate(v)
        if v and (self.SEPERATOR in v or self.HIGHEST_UNICODE in v):
            raise db.BadValueError(
                'Not all characters in property %s' % (self.name))
        return v

    def equals_filter(self, v):
        return self.name + ' =', IStringProperty._v2store(v)

    @classmethod
    def _v2store(cls, v):
        if v is None:
            return None
        if v.lower() == v:
            return v
        return v.lower() + cls.SEPERATOR + v

    def get_value_for_datastore(self, model_instance):
        v = getattr(model_instance, self.name)
        return IStringProperty._v2store(v)

    def make_value_from_datastore(self, value):
        if value is None:
            return value
        return value.split(self.SEPERATOR, 1)[-1]

class PickleProperty(db.BlobProperty):

    def validate(self, value):
        # accept everything
        try:
            pickle.dumps(value, -1)
        except pickle.PicklingError, err:
            raise db.BadValueError(
                'Property %r must be pickleable: (%s)' %
                            (self.name, err))

        return value

    def get_value_for_datastore(self, model_instance):
        v = getattr(model_instance, self.name)
        return self.data_type(pickle.dumps(v, -1))

    def make_value_from_datastore(self, value):
        if value is None:
            return value
        v = pickle.loads(str(value))
        return v


class SafeReferenceProperty(db.ReferenceProperty):
    """Doesn't raise an exception in case the referenced object can't be
       resolved.
    """

    def __get__(self, model_instance, model_class):
        try:
            return super(SafeReferenceProperty, self).__get__(
                                    model_instance, model_class)
        except datastore_errors.Error:
            if not self.required:
                error_msg = 'Unresolved Reference for "%s.%s" set to None'
                self.__set__(model_instance, None)
            else:
                error_msg = 'Unresolved Reference for "%s.%s" will remain ' \
                            'because it is required'
            _log.info(error_msg% (self.model_class.__name__,self._attr_name()))
            return None

