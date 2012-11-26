
import json
import hashlib
import urllib2
import urllib
from django.core.management.base import NoArgsCommand
from django.conf import settings

class Client(object):
  def __init__(self):
    self.service = settings.USERDBIMPORT_SERVICE
    self.secret = settings.USERDBIMPORT_SECRET
    self.endpoint = settings.USERDBIMPORT_ENDPOINT
    self.apiver = '1.4'

  def _get(self, **kwargs):
    data = {
      'apiver': self.apiver, 
      'service': self.service, 
      'output': 'JSON',
      'encoding': 'UTF-8',
      }
    if 'data' in kwargs:
      kwargs['data'] = json.dumps(kwargs['data'])
    else:
      kwargs['data'] = json.dumps({})
    data['data'] = kwargs['data']
    data['action'] = kwargs['action']
    data['checksum'] = self.checksum(**kwargs)

    url = '%s/?%s' % ( 
      self.endpoint, 
      '&'.join(['%s=%s'%(k,urllib.quote_plus(v)) for k,v in data.iteritems()]),
      )

#    print 'URL', url

    def do(url):
      data = urllib2.urlopen(url)
      result = json.loads(data.read())
      #print repr(result)
      return result['data']
      

    #return do(url)
    try:
      return do(url)
    except (urllib2.URLError, RuntimeError):
      return None

  def checksum(self, **kwargs):
    m = hashlib.md5()
    m.update(self.service)
    m.update(self.apiver)
    m.update(kwargs['action'])
    m.update(kwargs['data'])
    m.update(self.secret)
    return m.hexdigest()

  def get_organisations(self):
    return self._get(action='LIST_ORGANISATIONS')

  def get_users(self, **filter):
    return self._get(action='LIST_USERS', data=filter)

from dreamuserdb.models import Organisation, Role, Group
from django.contrib.auth.models import User
from django.db.utils import IntegrityError

def no_empty(value):
  if value == None or len(value) == 0:
    return ''
  return value

class Command(NoArgsCommand):
  def handle_noargs(self, *args, **kwargs):
    c = Client()

    if 0:
      orgs_data = c.get_organisations()
      for o in orgs_data:
        print 'ORGANISATION', o['name'], o['description']
        org, created = Organisation.objects.get_or_create(name=o['name'], title=o['description'])
        print '  ROLES'
        for r in o['roles']:
          print '  ', r['name']
          role, created = Role.objects.get_or_create(name=r['name'], title=r['name'], organisation=org)
        print '  GROUPS'
        for g in o['groups']:
          print '  ', g['name']
          group, created = Group.objects.get_or_create(name=r['name'], title=r['name'], organisation=org)

    if 1:
      for o in Organisation.objects.all():
        user_data = c.get_users(organisation=o.name)
        if user_data:
          print '  USERS'
          for u in user_data:
            print '  ', u['name']
            try:
              user, created = User.objects.get_or_create(
                username=u['name'], 
                first_name=no_empty(u['fname']), 
                last_name=no_empty(u['sname']), 
                email=no_empty(u['email'])
                )
            except IntegrityError:
              print 'INTEGRITY ERROR', repr(u)
            
            mu = user.user_set.get()
            if 0:
              if 'organisations' in u:
                mu.organisations = [Organisation.objects.get(name=uo['name']) for uo in u['organisations']]
            if 0:
              if 'roles' in u:
                uroles = []
                for ur in u['roles']:
                  if isinstance(ur, dict):
                    uroles.append(Role.objects.get(name=ur['name'], organisation__name=ur['organisation']['name']))
                mu.roles = uroles
            if 0:
              if 'groups' in u:
                ugroups = []
                for ug in u['groups']:
                  if isinstance(ug, dict):
                    ugroup, created = Group.objects.get_or_create(name=ug['name'], title=ug['name'], organisation=Organisation.objects.get(name=ug['organisation']['name']))
                    ugroups.append(ugroup)
                mu.groups = ugroups
            if 0:
              if u['mobilenum'] != None:
                mu.phone_number = u['mobilenum']
            if 1:
              if u['password'] != None:
                mu.password_md5 = u['password']
                #print mu.password_md5
            mu.save()
            #user.save()

