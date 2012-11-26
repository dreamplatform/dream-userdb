
import logging
import django.contrib.auth.models
from piston.handler import BaseHandler
from piston.utils import rc
from dreamuserdb import models

l = logging.getLogger(__name__)

try:
  from functools import wraps
except ImportError:
  from django.utils.functional import wraps  # Python 2.4 fallback.
from django.utils.decorators import available_attrs

def user_passes_test(test_func):
  def decorator(view_func):
    @wraps(view_func, assigned=available_attrs(view_func))
    def _wrapped_view(self, request, *args, **kwargs):
      if test_func(request.user):
        return view_func(self, request, *args, **kwargs)
      return rc.FORBIDDEN
    return _wrapped_view
  return decorator

def permission_required(perm):
  return user_passes_test(lambda u: u.has_perm(perm))

class RegisterService(BaseHandler):
  allowed_methods = ('POST',)

  def create(self, request):
    from django.contrib.auth.models import Permission
    perm_contenttype = ContentType.objects.get_for_model(models.Permission)
    # TODO How about namespaces by service?
    # TODO Validate p: can not contain space, dot or comma
    for p in request.data.permissions:
      perm, created = Permission.objects.get_or_create(name=p, codename=p, content_type=perm_contenttype)


class Permission(BaseHandler):
  allowed_methods = ('GET',)
  model = models.ServicePermission
  fields = (
    'name',
    )


class ByFilterHandler(BaseHandler):
  allowed_methods = ('GET',)
  
  def read(self, request, filter=None, id=None):
    if filter and id:
      return self.model.objects.filter(**{'%s__id'%filter: id})
    elif id:
      return self.model.objects.get(id=id)
    else:
      return self.model.objects.all()


class Role(ByFilterHandler):
  model = models.Role
  fields = (
    'id',
    'name',
    'title',
    'organisation',
    'permissions',
    'official',
    )


class Group(ByFilterHandler):
  model = models.Group
  exclude = ()


class Organisation(BaseHandler):
  allowed_methods = ('GET',)
  model = models.Organisation   
  exclude = ()

  def read(self, request, id=None):
    if id:
      return self.model.objects.get(id=id)
    else:
      return self.model.objects.all()


class User(BaseHandler):
  allowed_methods = ('GET','PUT')
  model = models.User
  exclude = ()
  fields = (
    'id',
    'username', 
    'first_name', 
    'last_name', 
    'email',
    'phone_number',
    'picture_url',
    'locale',
    'theme_color',
    'groups',
    'roles',
    'permissions',
    'organisations', 
    'saml_organisations',
    'saml_roles',
    'saml_permissions',
    'legacy_organisations',
    'legacy_roles',
    'saml_permissions',
    )

  @classmethod
  def groups(self, obj):
    return obj.user_groups.all()

  @classmethod
  def legacy_organisations(self, obj):
    return [o.name for o in obj.organisations.all()]

  @classmethod
  def legacy_roles(self, obj):
    return ['%s.%s'%(r.organisation.name,r.name) for r in obj.roles.all()]

  @classmethod
  def saml_organisations(self, obj):
    return [str(o.id) for o in obj.organisations.all()]

  @classmethod
  def saml_roles(self, obj):
    return [r.code for r in obj.roles.all()]

  @classmethod
  def saml_groups(self, obj):
    return [g.code for g in obj.groups.all()]

  @classmethod
  def saml_permissions(self, obj):
    perms = []
    for r in obj.roles.all():
      perms += r.permission_codes
    return perms

  def read(self, request, filter=None, id=None):
    if filter and id:
      return self.model.objects.filter(**{'%ss__id'%filter: id})
    if id:
      self.show_extra_fields = True
      return self.model.objects.get(pk=id)
    return self.model.objects.all()

  @permission_required('auth.change_user')
  def update(self, request, filter=None, id=None):
    if not request.content_type:
      return rc.BAD_REQUEST
    if not id:
      return rc.BAD_REQUEST
    if filter:
      return rc.BAD_REQUEST
    user = self.model.objects.get(pk=id)
    for k,v in request.data.iteritems():
      # Allow update to only these fields
      if k in ['first_name', 'last_name', 'email', 'phone_number', 'theme_color', 'picture_url']:
        setattr(user, k, v)
        l.debug('Update user %s.%s = %s' % (id, k, repr(v))) 
      if k == 'groups':
        user.user_groups = models.Group.objects.filter(id__in=[g['id'] for g in v])
        l.debug('Update user %s.%s = %s' % (id, k, repr(v)))
      elif k == 'roles':
        user.roles = models.Role.objects.filter(id__in=[g['id'] for g in v])
        l.debug('Update user %s.%s = %s' % (id, k, repr(v)))
      elif k == 'organisations':
        user.organisations = models.Organisation.objects.filter(id__in=[g['id'] for g in v])
        l.debug('Update user %s.%s = %s' % (id, k, repr(v)))
      elif k == 'password' and len(v) > 0 and 'password_check' in request.data:
        if user.check_password(request.data['password_check']):
            user.set_password(v)
        else:
            return rc.FORBIDDEN
        l.debug('Update user %s.%s = %s' % (id, k, repr(v)))
    user.save()
    return rc.ALL_OK


class Authenticate(User):
  allowed_methods = ('GET',)
  
  def read(self, request):
    from django.contrib.auth import authenticate
    user = authenticate(
      username=request.GET.get('username', None), 
      password=request.GET.get('password', None))
    if not user:
      return rc.FORBIDDEN
    return self.model.objects.get(id=user.id)

