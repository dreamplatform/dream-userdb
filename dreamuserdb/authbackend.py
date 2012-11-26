
import logging
import hashlib
from django.contrib.auth.backends import ModelBackend
from models import User

l = logging.getLogger(__name__)

class LegacyPasswordBackend(ModelBackend):

  def authenticate(self, **credentials):
    # Try old password
    pwhash = hashlib.md5()
    pwhash.update(credentials['password'])
    pwhash = pwhash.hexdigest()
    try:
      user = User.objects.get(
        password_md5=pwhash, 
        username=credentials['username'],
        password='')
    except User.DoesNotExist:
      return None
#    user.password_md5 = '!!!%s'%user.password_md5 # Disable old password
#    user.save()
    if user:
      user = user.user
    user.set_password(credentials['password'])
    user.save()
#    l.debug('Authenticated with legacy method: %s'%user)
    return user

