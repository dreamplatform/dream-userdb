
#encoding=utf-8

import base64
import json
from time import time
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.conf import settings

def http_auth(username='f', password='b'):
  credentials = base64.encodestring('%s:%s' % (username, password)).strip()
  auth_string = 'Basic %s' % credentials
  return auth_string

class Api1TestCase(TestCase):
  fixtures = ['api1_test_100_users.json', 'api1_test_user_1.json']

  def setUp(self):
    self.extra = {'HTTP_AUTHORIZATION': http_auth()}
    self.t = time()

  def tearDown(self):
    t = time() - self.t
    print repr(t)

class Api1GetAllUsersTestCase(Api1TestCase):

  def test_get_users(self):
    r = self.client.get('/api/1/user/', **self.extra)
    self.assertEqual(r.status_code, 200)
    print r.content

class Api1UserEditTestCase(Api1TestCase):
  
  def test_get_user(self):
    r = self.client.get('/api/1/user/1/', **self.extra)
    self.assertEqual(r.status_code, 200)
    print r.content

  def test_put_user(self):
    data = json.dumps({'first_name': 'foo'})
    r = self.client.put('/api/1/user/1/', data=data,
                        content_type='application/json', **self.extra)
    self.assertEqual(r.status_code, 200)

class Api1PerformanceTestCase(Api1TestCase):

  def _test_query_all_organisations(self):
    r = self.client.get('/api/1/organisation/', **self.extra)

  def _test_query_all_roles(self):
    r = self.client.get('/api/1/role/', **self.extra)

  def _test_query_all_groups(self):
    r = self.client.get('/api/1/group/', **self.extra)

  def _test_query_all_users(self):
    r = self.client.get('/api/1/user/', **self.extra)

  def test_repeat(self):
    for i in xrange(10):
      fs = (
        self._test_query_all_organisations,
        self._test_query_all_roles,
        self._test_query_all_groups,
        self._test_query_all_users,
        )
      for f in fs:
        t = time()
        f()
        t = time() - t
        print i, repr(f.__name__), repr(t)




