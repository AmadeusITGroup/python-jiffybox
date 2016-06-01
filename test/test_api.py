import datetime
import os
from six.moves import urllib

import pytest
import requests_mock

import jiffybox.api


HERE = os.path.abspath(os.path.dirname(__file__))

DUMMY_TOKEN = 'dummy_token'


@pytest.fixture()
def api():
    return jiffybox.api.JiffyBox(DUMMY_TOKEN)


class JiffyMock(requests_mock.Mocker):
    def add_response_fixture(self, method, data, *parts):
        body_path = os.path.join(HERE, 'fixtures', method, *parts) + '.json'
        with open(os.path.join(body_path),
                  'rb') as f:
            body = f.read()

        def text_cb(request, context):
            if data is not None:
                assert data == urllib.parse.parse_qs(request.body)
            return body

        self.register_uri(
            method, make_url('/'.join(parts)), status_code=200,
            headers={'Content-Type': 'application/json'}, text=text_cb)


@pytest.fixture()
def jiffy_mock():
    return JiffyMock()


def make_url(endpoint):
    return 'https://api.jiffybox.de/{0}/v1.0/{1}'.format(
        DUMMY_TOKEN, endpoint)


def test_invalid_api_module(api, jiffy_mock):
    with jiffy_mock as m:
        m.add_response_fixture('GET', None, 'test')

        with pytest.raises(jiffybox.api.JiffyMessageException) as e:
            api._get('test')

        messages, response = e.value
        assert messages == [{
            'type': 'error',
            'message': 'Das Modul test existiert nicht'
        }]
        assert response.status_code == 200


def test_box_list(api, jiffy_mock):
    with jiffy_mock as m:
        m.add_response_fixture('GET', None, 'jiffyBoxes')

        boxes = api.boxes()
        assert isinstance(boxes, list)
        box = boxes[0]
        assert box.id == 12345
        assert box.ips['public'] == ['188.93.14.176']
        assert isinstance(box.plan, jiffybox.api.Plan)
        assert box.plan.id == 22
        assert box.created == datetime.datetime(2009, 2, 13, 23, 31, 30)


def test_box(api, jiffy_mock):
    with jiffy_mock as m:
        m.add_response_fixture('GET', None, 'jiffyBoxes', '12345')

        b = api.box('12345')
        assert b.id == 12345


def test_box_delete(api, jiffy_mock):
    with jiffy_mock as m:
        m.add_response_fixture('DELETE', None, 'jiffyBoxes', '12345')

        assert api.delete_box('12345')

    with jiffy_mock as m:
        m.add_response_fixture('GET', None, 'jiffyBoxes', '12345')
        m.add_response_fixture('DELETE', None, 'jiffyBoxes', '12345')

        b = api.box('12345')
        assert b.delete()


def test_box_create(api, jiffy_mock):
    with jiffy_mock as m:
        m.add_response_fixture('POST', {
            'distribution': ['centos_5_4_64bit'],
            'name': ['Test'],
            'planid': ['10'],
        }, 'jiffyBoxes')

        b = api.create_box('Test', 10, distribution='centos_5_4_64bit')

        assert b.id == 12345
        assert b.status == 'CREATING'
