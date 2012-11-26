
from dreamuserdb.models import User

class InsertDreamUser(object):
    """Inserts Dream User to variable normally containing framework user, if possible
    """
    def process_request(self, request):
        if request.user.is_authenticated():
            try:
                duser = User.objects.get(pk=request.user.pk)
                request.user = duser
            except User.DoesNotExist:
                pass
        return None
