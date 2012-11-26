
# FIXME: Commented out since dreamuserdn.models does not have class DjangoPermission
#import csv
#import codecs
#from django.core.management.base import BaseCommand
#from django.conf import settings
#from django.contrib.auth.models import Permission, User as DjangoUser
#from django.db import IntegrityError
#from dreamuserdb.models import DjangoPermission, Organisation, Role, Group

C_ORGANISATION = 1
C_ROLE = 10
C_USER = 100

#class Command(BaseCommand):
#  def handle(self, *args, **kwargs):
#    for o in xrange(C_ORGANISATION):
#      o = str(o)
#      org = Organisation(name=o, title=o)
#      org.save()
#
#      for r in xrange(C_ROLE):
#        r = str(r)
#        role = Role(name=r, organisation=org)
#        role.save()
#        role.permissions = DjangoPermission.objects.all()
#
#      for u in xrange(10, 10+C_USER):
#        u = str(u)
#        user = DjangoUser(username=u, password=u, email='%s@%s.%s%s'%(u,u,u,u))
#        user.save()
#        profile = user.get_profile()
#        profile.roles = Role.objects.filter(organisation=org)
#        profile.organisations.add(org)

