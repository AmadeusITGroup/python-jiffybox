import requests
import datetime
import time
import logging

from .exceptions import JiffyAttributeException, JiffyMessageException

_logger = logging.getLogger(__name__)


class _JiffyObject(object):
    _attributes = {}

    def __init__(self, json, api=None, id_=None):
        self.api = api
        self._json_data = json

        for attr_name, options in self._attributes.items():
            json_value = self._json_data.get(attr_name)

            optional = options and options.get('optional')
            filter = options and options.get('filter')

            if json_value is None and not optional:
                raise JiffyAttributeException(attr_name, json_value,
                                              self._json_data, type(self))

            if filter is not None and json_value is not None:
                setattr(self, attr_name, filter(json_value))
            else:
                setattr(self, attr_name, json_value)

        # FIXME
        if not hasattr(self, 'id') and id_ is not None:
            self._json_data['id'] = id_
            setattr(self, 'id', id_)

    @staticmethod
    def _time_from_epoch(timestamp):
        return datetime.datetime.fromtimestamp(timestamp)

    def _json_value(self, name):
        return self._json_data[name]

    def __repr__(self):
        return str(self._json_data)

    @property
    def json(self):
        return self._json_data


class _JiffyResource(_JiffyObject):

    @classmethod
    def _extract_results(cls, response):
        response.raise_for_status()
        if callable(response.json):
            json = response.json()
        else:
            json = response.json
        messages = json['messages']

        if messages:
            raise JiffyMessageException(messages, response)

        return json['result']

    def _get(self, endpoint=''):
        return self.api._get(self._api_location, endpoint)

    def _post(self, data=None, endpoint=''):
        return self.api._post(self._api_location, data, endpoint)

    def _put(self, data=None, endpoint=''):
        return self.api._put(self._api_location, data, endpoint)

    @classmethod
    def all(cls, api):
        res = api._get(cls._api_location)
        return [cls(json_, api=api, id_=id_) for id_, json_ in res.items()]

    @classmethod
    def find(cls, api, id):
        res = api._get(cls._api_location, str(id))
        return cls(res, api=api)

    def delete(self):
        raise Exception('No dawg')


class Plan(_JiffyResource):
    """
    A plan
    """
    _attributes = {'cpus': None,
                   'diskSizeInMB': None,
                   'id': {'filter': str},
                   'name': None,
                   'pricePerHour': None,
                   'pricePerHourFrozen': None,
                   'ramInMB': None,
                   }
    _api_location = 'plans'

    def __str__(self):
        return '<Plan {0}: {1}>'.format(self.id, self.name)


class Distribution(_JiffyResource):
    """
    A distribution
    """
    _attributes = {'minDiskSizeMB': None,
                   'name': None,
                   'rootdiskMode': None,
                   'defaultKernel': None,
                   }
    _api_location = 'distributions'


class Disk(_JiffyObject):
    """
    A disk
    """
    _attributes = {'filesystem': None,
                   'name': None,
                   'sizeInMB': None,
                   'status': None,
                   'distribution': {
                       'optional': True,
                   },
                   'created': {
                       'filter': _JiffyObject._time_from_epoch,
                   },
                   }


class Profile(_JiffyObject):
    """
    A profile
    """
    _attributes = {'kernel': None,
                   'name': None,
                   'rootdisk': None,
                   'rootdiskMode': None,
                   'runlevel': None,
                   'status': None,
                   'created': {
                       'filter': _JiffyObject._time_from_epoch,
                   },
                   'disks': {
                       'filter': lambda d:
                       dict([(key, Disk(value)) for key, value in d.items()]),
                   }
                   }


class Box(_JiffyResource):
    """
    A single JiffyBox
    """
    _attributes = {'id': None,
                   'metadata': None,
                   'isBeingCopied': None,
                   'manualBackupRunning': None,
                   'name': None,
                   'recoverymodeActive': None,
                   'running': None,
                   'status': None,
                   'ips': None,
                   'host': {'optional': True},
                   'runningSince': {
                       'filter': _JiffyObject._time_from_epoch,
                       'optional': True,
                   },
                   'created': {
                       'filter': _JiffyObject._time_from_epoch,
                   },
                   'plan': {'filter': Plan},
                   'activeProfile': {
                       'filter': Profile,
                       'optional': True,
                   },
                   }

    _statuses = set(['START', 'SHUTDOWN', 'PULLPLUG', 'FREEZE', 'THAW',
                     'UPDATING', 'FREEZING', 'THAWING', 'READY', 'FROZEN'])

    _api_location = 'jiffyBoxes'

    def __str__(self):
        return '<Box {0}: {1}>'.format(self.id, self.name)

    @classmethod
    def create(cls, api, name, plan, backupid=None, distribution=None,
               password=None, use_sshkey=None, metadata=None):
        """
        Create a new box.

        :param api: API object to use
        :type api: :class:`JiffyBox`

        :param name: Display name of the new box
        :type name: string

        :param plan: Plan to use
        :type plan: :class:`Plan` or ID of an available  plan

        :param backupid: ID to use for backups
        :type backupid: string

        :param distribution: Distribution to use
        :type distribution: :class:`Distribution` or ID an available
                            distribution

        :param password: Password for the new box
        :type password: string

        :param use_sshkey: Whether to install SSH keys
        :type use_sshkey: bool

        :param metadata: additional metadata to attach
        :type metadata: dict

        :rtype: :class:`Box`
        """

        if isinstance(plan, Plan):
            plan = plan.id

        data = {
            'name': name,
            'planid': plan,
        }

        if distribution:
            if isinstance(distribution, Distribution):
                distribution = distribution.id

            data['distribution'] = distribution

        if use_sshkey is not None:
            data['use_sshkey'] = use_sshkey

        if metadata is not None:
            data['metadata'] = metadata

        res = api._post(cls._api_location, data=data)
        return cls(res, api)

    @property
    def ready(self):
        return self.status == 'READY'

    def wait_for_status(self, status='READY', max_wait=60, poll_interval=7):
        # FIXME allow timedelta as params
        end = datetime.datetime.now() + datetime.timedelta(seconds=max_wait)

        while end > datetime.datetime.now():
            next = self.find(self.api, self.id)  # use self.update()

            if next.status == status:
                return next

            time.sleep(poll_interval)

    def start(self):
        # FIXME use update
        res = self._put(endpoint=self.id, data={'status': 'START'})
        return type(self)(res, self.api)

    @property
    def public_ips(self):
        return self.ips.get('public', None)

    @property
    def private_ips(self):
        return self.ips.get('private', None)


class JiffyBox(object):
    """
    Entrypoint to the JiffyBox API. Represents a single account.

    :param api_key: API key
    :type api_key: string
    """
    def __init__(self, api_key, api_url='https://api.jiffybox.de',
                 api_version='v1.0'):
        self._api_key = api_key
        self.api_url = api_url
        self.api_version = api_version
        self._connection = requests.Session()

    def box(self, id):
        """
        Get information of a specific box.

        :param id: ID of the box
        :type id: string
        :rtype: :class:`Box`
        """
        return Box.find(self, id)

    def boxes(self):
        """
        List all boxes in the account.

        :rtype: List of :class:`boxes <Box>`
        """
        return Box.all(self)

    def distribution(self, id):
        """
        Get information of a specific distribution.

        :param id: ID of the distribution
        :type id: string
        :rtype: :class:`Distribution`
        """
        return Distribution.find(self, id)

    def distributions(self):
        """
        List all available distributions.

        :rtype: List of :class:`distributions <Distribution>`
        """
        return Distribution.all(self)

    def plan(self, id):
        """
        Get information of a specific plan.

        :param id: ID of the distribution
        :type id: string
        :rtype: :class:`Plan`
        """
        return Plan.find(self, id)

    def plans(self):
        """
        List all available plans.

        :rtype: List of :class:`plans <Plan>`
        """
        return Plan.all(self)

    def create_box(self, *args, **kwargs):
        """
        Create a new box

        For parameters see :meth:`Box.create`.

        :rtype: :class:`Box`
        """
        return Box.create(self, *args, **kwargs)

    def _get(self, api_location, endpoint=''):
        url = self._make_url(api_location, endpoint)
        _logger.debug('GET: {0}'.format(url))
        res = self._connection.get(url)
        return self._extract_results(res)

    def _post(self, api_location, data=None, endpoint=''):
        url = self._make_url(api_location, endpoint)
        _logger.debug('POST: {0} , data: {1}'.format(url, data))
        res = self._connection.post(url, data=data)
        return self._extract_results(res)

    def _put(self, api_location, data=None, endpoint=''):
        url = self._make_url(api_location, endpoint)
        _logger.debug('PUT: {0} , data: {1}'.format(url, data))
        res = self._connection.put(url, data=data)
        return self._extract_results(res)

    @staticmethod
    def _extract_results(response):
        response.raise_for_status()
        if callable(response.json):
            json = response.json()
        else:
            json = response.json
        messages = json['messages']

        if messages:
            raise JiffyMessageException(messages, response)

        return json['result']

    def _make_url(self, api_location, endpoint=''):
        endpoint = str(endpoint)
        return '/'.join([self.api_url, self._api_key, self.api_version,
                         api_location, endpoint])
