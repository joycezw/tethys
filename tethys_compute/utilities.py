"""
********************************************************************************
* Name: utilities.py
* Author: Scott Christensen
* Created On: 2015
* Copyright: (c) Brigham Young University 2015
* License: BSD 2-Clause
********************************************************************************
"""

import json
from django import forms
from django.core import exceptions
from django.db import models
from django.utils.translation import ugettext_lazy as _

# TODO this should be refactored so it doesn't rely on the depricated code which I've copied here from the Django source
# see https://code.djangoproject.com/ticket/26807

# deprecated code copied from: https://github.com/django/django/blob/stable/1.9.x/django/db/models/fields/subclassing.py

class SubfieldBase(type):
    """
    A metaclass for custom Field subclasses. This ensures the model's attribute
    has the descriptor protocol attached to it.
    """
    def __new__(cls, name, bases, attrs):

        new_class = super(SubfieldBase, cls).__new__(cls, name, bases, attrs)
        new_class.contribute_to_class = make_contrib(
            new_class, attrs.get('contribute_to_class')
        )
        return new_class


class Creator(object):
    """
    A placeholder class that provides a way to set the attribute on the model.
    """
    def __init__(self, field):
        self.field = field

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        return obj.__dict__[self.field.name]

    def __set__(self, obj, value):
        obj.__dict__[self.field.name] = self.field.to_python(value)


def make_contrib(superclass, func=None):
    """
    Returns a suitable contribute_to_class() method for the Field subclass.
    If 'func' is passed in, it is the existing contribute_to_class() method on
    the subclass and it is called before anything else. It is assumed in this
    case that the existing contribute_to_class() calls all the necessary
    superclass methods.
    """
    def contribute_to_class(self, cls, name, **kwargs):
        if func:
            func(self, cls, name, **kwargs)
        else:
            super(superclass, self).contribute_to_class(cls, name, **kwargs)
        setattr(cls, self.name, Creator(self))

    return contribute_to_class


# code for DictionaryField was taken from https://djangosnippets.org/snippets/1979/

class DictionaryField(models.Field):
    description = _("Dictionary object")

    __metaclass__ = SubfieldBase

    def get_internal_type(self):
        return "TextField"

    def to_python(self, value):
        if value is None:
            return None
        elif value == "":
            return {}
        elif isinstance(value, basestring):
            try:
                return dict(json.loads(value))
            except (ValueError, TypeError):
                raise exceptions.ValidationError(self.error_messages['invalid value for json: %s' % value])

        if isinstance(value, dict):
            return value
        else:
            return {}

    def from_db_value(self, value,  expression, connection, context):
        return self.to_python(value)

    def get_prep_value(self, value):
        if not value:
            return ""
        elif isinstance(value, basestring):
            return value
        else:
            return json.dumps(value)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_prep_value(value)

    def clean(self, value, model_instance):
        value = super(DictionaryField, self).clean(value, model_instance)
        return self.get_prep_value(value)

    def formfield(self, **kwargs):
        defaults = {'widget': forms.Textarea}
        defaults.update(kwargs)
        return super(DictionaryField, self).formfield(**defaults)

class ListField(models.Field):
    description = _("List object")

    __metaclass__ = SubfieldBase

    def get_internal_type(self):
        return "TextField"

    def to_python(self, value):
        if value is None:
            return None
        elif value == "":
            return []
        elif isinstance(value, basestring):
            try:
                return json.loads(value)
            except (ValueError, TypeError) as e:
                raise e
                #raise exceptions.ValidationError(self.error_messages['invalid value for json: %s' % value])

        if isinstance(value, list):
            return value
        else:
            return []

    def from_db_value(self, value, expression, connection, context):
        return self.to_python(value)

    def get_prep_value(self, value):
        if not value:
            return ""
        elif isinstance(value, basestring):
            return value
        else:
            return json.dumps(value)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_prep_value(value)

    def clean(self, value, model_instance):
        value = super(ListField, self).clean(value, model_instance)
        return self.get_prep_value(value)

    def formfield(self, **kwargs):
        defaults = {'widget': forms.Textarea}
        defaults.update(kwargs)
        return super(ListField, self).formfield(**defaults)