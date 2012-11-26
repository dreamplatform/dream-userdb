
import logging
from django.conf.urls.defaults import *
from piston.resource import Resource as R
from piston.authentication import HttpBasicAuthentication
import handlers

l = logging.getLogger(__name__)

class Auth(HttpBasicAuthentication):
  def is_authenticated(self, request):
    user = super(Auth, self).is_authenticated(request)
    if user and request.user.has_perm('dreamuserdb.api'):
      return user
    return False

auth = Auth(realm='UserDB API')
organisation = R(handlers.Organisation, auth)
group = R(handlers.Group, auth)
role = R(handlers.Role, auth)
user = R(handlers.User, auth)
authenticate = R(handlers.Authenticate, auth)

urlpatterns = patterns('',
   url(r'^organisation/(?P<id>[^/]+)/$', organisation),
   url(r'^organisation/$', organisation),
   url(r'^role/(?P<filter>organisation)/(?P<id>[^/]+)/$', role),
   url(r'^role/(?P<id>[^/]+)/$', role),
   url(r'^role/$', role),
   url(r'^group/(?P<filter>organisation)/(?P<id>[^/]+)/$', group),
   url(r'^group/(?P<id>[^/]+)/$', group),
   url(r'^group/$', group),
   url(r'^user/(?P<filter>organisation)/(?P<id>[^/]+)/$', user),
   url(r'^user/(?P<filter>role)/(?P<id>[^/]+)/$', user),
   url(r'^user/(?P<filter>group)/(?P<id>[^/]+)/$', user),
   url(r'^user/(?P<id>[^/]+)/$', user),
   url(r'^user/$', user),

   # Authenticate
   url(r'^authenticate/$', authenticate),
)

