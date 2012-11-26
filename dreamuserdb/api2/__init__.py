
# coding=utf-8

from tastypie.api import Api
from resources import UserResource, GroupResource, RoleResource, OrganisationResource, AuthenticateResource

api = Api(api_name='2')
api.register(UserResource())
api.register(GroupResource())
api.register(RoleResource())
api.register(OrganisationResource())
api.register(AuthenticateResource())

urls = api.urls
