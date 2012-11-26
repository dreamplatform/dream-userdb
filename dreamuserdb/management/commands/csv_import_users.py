# -*- coding: utf-8 -*-

import csv
import codecs
from optparse import make_option
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from dreamuserdb.models import User, Organisation, Role, Group

class Command(BaseCommand):
  option_list = BaseCommand.option_list + (
    make_option('--override',
        action='store_true',
        dest='override',
        default=False,
        help='Override data in database'),
    make_option('--verbose',
        action='store_true',
        dest='verbose',
        default=False,
        help='Verbose'),
    make_option('--only-update',
        action='store_true',
        dest='only_update',
        default=False,
        help='Do not create new users'),
    )

  def handle(self, *args, **options):
    self.override = options['override']
    self.verbose = options['verbose']
    self.only_update = options['only_update']
    csv_data = csv.reader(codecs.open(args[0], 'rb'), delimiter=',', quotechar='"')
    for r in csv_data:
      data = {
        'username': r[0],
        'first_name': r[1],
        'last_name': r[2],
        'phone_number': r[3],
        'email': r[4],
        'organisation': r[5],
        'group': r[6],
        'role': r[7],
        }
      if len(r) > 8:
        data['password'] = r[8]
      try:
        if self.verbose:
          print repr(data)
        result = self.create_user(data.copy())
      except IntegrityError:
        print "ERR", repr(data)
      except ObjectDoesNotExist:
        print "ERR", repr(result)

  def create_username(self, data):
      u = u'%s.%s' % (data['first_name'].decode('utf-8'), data['last_name'].decode('utf-8'))
      u = u.lower()
      u = u.replace(' ', '.')
      u = u.replace('-', '')
      u = u.replace(u'ä', 'a')
      u = u.replace(u'ö', 'o')
      return u

  def create_user(self, data):
    data['organisation'], c = Organisation.objects.get_or_create(name=data['organisation'], defaults={'title': data['organisation']})
    if c or self.override:
      data['organisation'].save()
      print "ORGANISATION", repr(data['organisation'])

    if data['group']:
      data['group'], c = Group.objects.get_or_create(name=data['group'], organisation=data['organisation'], defaults={'title': data['group'], 'official': True})
      if c or self.override:
        data['group'].save()
      	print "GROUP", repr(data['group'])

    if data['role']:
      data['role'], c = Role.objects.get_or_create(name=data['role'], organisation=data['organisation'], defaults={'title': data['role']})
      if c or self.override:
        data['role'].save()
      	print "ROLE", repr(data['role'])

    if not data['username']:
      data['username'] = self.create_username(data)

    if self.only_update:
      user = User.objects.get(username=data['username'])
      c = False
    else:
      user,c = User.objects.get_or_create(username=data['username'])

    if c or self.override:
      print "USER", user.id, repr(user.username), repr(user)
      user.first_name = data['first_name']
      user.last_name = data['last_name']
      user.email = data['email']
      if 'password' in data:
        user.set_password(data['password'])
      user.phone_number = data['phone_number']
      user.organisations.clear()
      user.roles.clear()
      user.user_groups.clear()
      user.save()

      if data['organisation']:
        user.organisations.add(data['organisation'])
      if data['role']:
        user.roles.add(data['role'])
      if data['group']:
        user.user_groups.add(data['group'])
    return data

