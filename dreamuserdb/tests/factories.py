
# -*- encoding: utf-8 -*-

import factory  # this needs factory-boy installed
from dreamuserdb import models as dm

class UserFactory(factory.Factory):
  FACTORY_FOR = dm.User

  first_name = 'Teppo'
  last_name = 'Testaaja'
  email = factory.LazyAttribute(lambda a: '{0}.{1}@haltu.fi'.format(a.first_name, a.last_name).lower())
  username = factory.LazyAttributeSequence(lambda a, n: '{0}{1}'.format(a.first_name.lower(), n))
  password = first_name.lower()

  @classmethod
  def _prepare(cls, create, **kwargs):
    password = kwargs.pop('password', None)
    user = super(UserFactory, cls)._prepare(create, **kwargs)
    if password:
      user.set_password(password)
      if create:
        user.save()
      return user


# vim: tabstop=2 expandtab shiftwidth=2 softtabstop=2

