from .exceptions import JiffyAttributeException


class _JiffyObjectAttribute(object):
    def __init__(self, name, optional, filter):
        self.name = name
        self.optional = optional
        self.filter = filter
        self.__doc__ = 'JSON-Field `{}`'.format(name)

    def __get__(self, obj, type=None):
        if obj is None:
            return self

        json_value = obj._json_data.get(self.name)
        if json_value is None and not self.optional:
            raise JiffyAttributeException(self.name, json_value,
                                          self._json_data, type(self))

        if self.filter is not None and json_value is not None:
            return self.filter(json_value)
        return json_value


class _JiffyObjectMeta(type):
    def __new__(metaclass, name, parents, final_attrs):

        attr_spec = final_attrs.pop('_attributes', {})

        for attr_name, options in attr_spec.items():
            optional = options and options.get('optional', True)
            filter = options and options.get('filter')
            final_attrs[attr_name] = _JiffyObjectAttribute(
                 attr_name, optional, filter,
            )

        if final_attrs.get('id') is None:
            final_attrs['id'] = _JiffyObjectAttribute(
                'id', False, None,
            )

        return type.__new__(metaclass, name, parents, final_attrs)
