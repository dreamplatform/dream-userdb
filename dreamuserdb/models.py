
import logging
from django.db import models
from django.utils.translation import ugettext_lazy as _
import django.contrib.auth.models
from django.db.models.signals import post_save

l = logging.getLogger(__name__)

def on_new_user_created(sender, **kwargs):
    if kwargs['created']:
        user = kwargs['instance']
        duser = User(user_ptr_id=kwargs['instance'].pk)
        duser.__dict__.update(user.__dict__)
        duser.save()

post_save.connect(on_new_user_created, sender=django.contrib.auth.models.User)



class ServicePermission(models.Model):
  name = models.CharField(max_length=200, editable=False, null=True)
  service = models.CharField(max_length=200)
  entity = models.CharField(max_length=200)
  action = models.CharField(max_length=200)

  def save(self, *args, **kwargs):
    self.name = u'%s.%s.%s' % (self.service, self.entity, self.action)
    super(ServicePermission, self).save(*args, **kwargs)

  def __unicode__(self):
    return self.name


class Organisation(models.Model):
  name = models.CharField(max_length=200) # TODO Should be removed
  title = models.CharField(max_length=200)

  def __unicode__(self):
    return self.title


class Group(models.Model):
  name = models.CharField(max_length=200) # TODO Should be removed
  title = models.CharField(max_length=200)
  organisation = models.ForeignKey(Organisation)
  official = models.BooleanField(default=False)

  class Meta:
    unique_together = ('name', 'organisation')

  @property
  def code(self):
    return '%s.%s'%(self.organisation.id, self.id)

  def __unicode__(self):
    return "%s / %s" % (self.title, self.organisation.title)


class Role(models.Model):
  name = models.CharField(max_length=200) # TODO Should be removed
  title = models.CharField(max_length=200)
  organisation = models.ForeignKey(Organisation)
  permissions = models.ManyToManyField(ServicePermission)
  official = models.BooleanField(default=False)

  class Meta:
    unique_together = ('name', 'organisation')
    permissions = (
      ('api', 'Can use UserDB API'),
    )

  @property
  def code(self):
    return '%s.%s'%(self.organisation.id, self.id)

  @property
  def permission_codes(self):
    return ['%s.%s'%(self.code,p.name) for p in self.permissions.all()]

  def __unicode__(self):
    return "%s / %s" % (self.title, self.organisation.title)

import re
USERNAME_RE = re.compile(r'^[a-z0-9-_\.]+$')

class User(django.contrib.auth.models.User):
  roles = models.ManyToManyField(Role, blank=True)
  user_groups = models.ManyToManyField(Group, blank=True)
  organisations = models.ManyToManyField(Organisation, blank=True)
  phone_number = models.CharField(max_length=200, blank=True)
  theme_color = models.CharField(max_length=8, blank=True, null=True, default='ffffff')
  picture_url = models.TextField(blank=True, null=True)
  password_md5 = models.CharField(max_length=50, null=True, blank=True)

  # TODO locale should be field
  @property
  def locale(self):
    return 'fi-fi'

  def clean(self):
      super(User, self).clean()
      valid = self._is_username_valid()
      if not valid:
          from django.core.exceptions import ValidationError
          raise ValidationError(_(u'Wrong format in username'))

  def _is_username_valid(self):
      match = USERNAME_RE.match(self.username)
      if match and not '..' in self.username:
          return True
      return False

  def save(self, *args, **kwargs):
      valid = self._is_username_valid()
      if not valid:
          raise Exception('Wrong format in username')
      return super(User, self).save(*args, **kwargs)

class AuthProvider(models.Model):
    organisation = models.ForeignKey(Organisation, related_name='auth_providers')
