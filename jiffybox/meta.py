from .exceptions import JiffyAttributeException


class _JiffyObjectAttribute(object):
    def __init__(self, name, optional, filter, fallback_attr=None):
        self.name = name
        self.optional = optional
        self.filter = filter
        self.fallback_attr = fallback_attr
        self.__doc__ = 'JSON-Field `{0}`'.format(name)

    def __get__(self, obj, type=None):
        if obj is None:
            return self

        value = obj._json_data.get(self.name)

        if value is None and self.fallback_attr:
            value = obj.get(self.fallback_attr)

        if value is None and not self.optional:
            raise JiffyAttributeException(self.name, value,
                                          self._json_data, type(self))

        if self.filter is not None and value is not None:
            return self.filter(value)
        return value


class _JiffyObjectMeta(type):
    def __new__(metaclass, name, parents, final_attrs):

        attr_spec = final_attrs.pop('_attributes', {})

        for attr_name, options in attr_spec.items():
            optional = options and options.get('optional', True)
            filter = options and options.get('filter')
            final_attrs[attr_name] = _JiffyObjectAttribute(
                 attr_name, optional, filter,
            )

        final_attrs['id'] = _JiffyObjectAttribute(
            'id', False, None, '_upstream_id',
        )

        return type.__new__(metaclass, name, parents, final_attrs)
