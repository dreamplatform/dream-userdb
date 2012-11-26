
# -*- coding: utf-8 -*-

from tastypie.authentication import BasicAuthentication
from tastypie.authorization import Authorization
from tastypie.resources import ModelResource
from tastypie import fields
from tastypie.exceptions import ImmediateHttpResponse
from tastypie.constants import ALL_WITH_RELATIONS
from django.http import HttpResponse
from django.db.models import related
from dreamuserdb.models import User, Group, Role, Organisation, ServicePermission


class Api2Auth(BasicAuthentication):
    def is_authenticated(self, request, **kwargs):
        authenticated =  super(Api2Auth, self).is_authenticated(request, **kwargs)
        if authenticated and request.user.has_perm('dreamuserdb.api'):
            return True
        return False


class UserResourceAuthorization(Authorization):
    def is_authorized(self, request, object=None):
        return request.user.has_perm('auth.change_user')


class BaseResource(ModelResource):
    def determine_format(self, request):
        return 'application/json'

    '''
    def obj_to_dict(self, obj):
        """
        Return obj as json serializeable python dict presentation.
        Handles ForeignKey and ManyToMany fields by recursive calls.
        """
        data = {}
        fields = obj._meta.fields + obj._meta.many_to_many
        for field in fields:
            value = getattr(obj, field.name)
            if isinstance(field, related.ForeignKey) or isinstance(field, related.OneToOneField):
                value = self.obj_to_dict(getattr(obj, field.name))
            elif isinstance(field, related.ManyToManyField):
                l = getattr(obj, field.name).all()
                value = [self.obj_to_dict(o) for o in l]
            else:
                value = getattr(obj, field.name)
            data[field.name] = value
        return data
    '''

    def build_filters(self, filters=None):
        """
        Overrides filter building from qs params. Fixes bug in tastypie which
        disables giving list parameters to __in and __range filters with '1,2,3' syntax
        """
        qs_filters = super(BaseResource, self).build_filters(filters)
        for k, v in qs_filters.iteritems():
            if isinstance(v, (list, tuple)) and len(v) == 1:
                i = v[0]
                i = i.split(',')
                qs_filters[k] = i
        return qs_filters

    class Meta:
        authentication = Api2Auth()
        auhorization = Authorization()
        list_allowed_methods = ('get',)
        detail_allowed_methods = ('get',)
        limit = 0 #this disables pagination, TODO remove this line when pagination is wanted


class PermissionResource(BaseResource):
    class Meta(BaseResource.Meta):
        fields = ('name', 'id')
        queryset = ServicePermission.objects.all()
        filtering = {
            'name' : ALL_WITH_RELATIONS,
            'id' : ALL_WITH_RELATIONS,
        }


#these are exposed in api

class GroupResource(BaseResource):
    organisation = fields.ToOneField('dreamuserdb.api2.resources.OrganisationResource',\
            'organisation', full=True)

    class Meta(BaseResource.Meta):
        queryset = Group.objects.all().select_related()
        filtering = {
            'name' : ALL_WITH_RELATIONS,
            'organisation' : ALL_WITH_RELATIONS,
            'id' : ALL_WITH_RELATIONS,
            'official' : ALL_WITH_RELATIONS,
        }


class RoleResource(BaseResource):
    organisation = fields.ToOneField('dreamuserdb.api2.resources.OrganisationResource',\
            'organisation', full=True)
    permissions = fields.ToManyField(PermissionResource, 'permissions', full=True)

    class Meta(BaseResource.Meta):
        queryset = Role.objects.all().select_related()
        filtering = {
            'id' : ALL_WITH_RELATIONS,
            'name' : ALL_WITH_RELATIONS,
            'permissions' : ALL_WITH_RELATIONS,
        }


class OrganisationResource(BaseResource):
    class Meta:
        queryset = Organisation.objects.all().select_related()
        filtering = {
            'id' : ALL_WITH_RELATIONS,
        }


class UserResource(BaseResource):
    user_groups = fields.ToManyField(GroupResource, 'user_groups', full=True)
    roles = fields.ToManyField(RoleResource, 'roles', full=True)
    organisations = fields.ToManyField(OrganisationResource, 'organisations', full=True)

    #These are optimization stuff, currently these will break filtering thus are disabled
    #user_groups = fields.ListField()
    #roles = fields.ListField('roles')
    #organisations = fields.ListField()

    #def dehydrate_user_groups(self, bundle):
    #    return [self.obj_to_dict(g) for g in bundle.obj.user_groups.all()]

    #def dehydrate_roles(self, bundle):
    #    return [self.obj_to_dict(r) for r in bundle.obj.roles.all()]

    #def dehydrate_organisations(self, bundle):
    #    return [self.obj_to_dict(o) for o in bundle.obj.organisations.all()]

    #def check_filtering(self, field_name, filter_type='exact', filter_bits=None):
    #    #be vary of these when applying new filtering stuff
    #    if field_name == 'user_groups':
    #        return ['user_groups__id']
    #    elif field_name == 'roles':
    #        return ['roles__id', 'roles_permissions__name']
    #    elif field_name == 'organisations':
    #        return ['organisations__id']
    #    else:
    #        return super(UserResource, self).check_filtering(field_name, filter_type, filter_bits)

    def obj_update(self, bundle, request=None, **kwargs):
        if not 'pk' in kwargs:
            return ImmediateHttpResponse(HttpResponse(status=400))

        user = self._meta.queryset.get(pk=kwargs['pk'])

        for k,v in bundle.data.iteritems():
            # Allow update to only these fields
            if k in ['first_name', 'last_name', 'email', 'phone_number', 'theme_color', 'picture_url']:
                setattr(user, k, v)
            elif k == 'user_groups':
                user.user_groups = Group.objects.filter(id__in=[g['id'] for g in v])
            elif k == 'roles':
                user.roles = Role.objects.filter(id__in=[g['id'] for g in v])
            elif k == 'organisations':
                user.organisations = Organisation.objects.filter(id__in=[g['id'] for g in v])
            elif k == 'password' and len(v) > 0 and 'password_check' in bundle.data:
                if user.check_password(bundle.data['password_check']):
                    user.set_password(v)
                else:
                    raise ImmediateHttpResponse(HttpResponse(status=403))
        user.save()

    class Meta(BaseResource.Meta):
        allowed_methods = ('get', 'put',) #read and modify
        queryset = User.objects.select_related().all()
        fields = ('id', 'username', 'phone_number', 'theme_color', 'first_name', 'last_name', 'picture_url', 'email',)
        detail_allowed_methods = ('get', 'put',)
        authorization = UserResourceAuthorization()
        filtering = {
            'user_groups' : ALL_WITH_RELATIONS,
            'roles' : ALL_WITH_RELATIONS,
            'organisations' : ALL_WITH_RELATIONS,
        }


class AuthenticateResource(BaseResource):
    legacy_organisations = fields.ListField(readonly=True)
    legacy_roles = fields.ListField(readonly=True)
    saml_organisations = fields.ListField(readonly=True)
    saml_roles = fields.ListField(readonly=True)
    saml_permissions = fields.ListField(readonly=True)
    locale = fields.CharField(readonly=True, default='fi-fi')

    def dehydrate_legacy_organisations(self, bundle):
        return [org.name for org in bundle.obj.organisations.all()]

    def dehydrate_legacy_roles(self, bundle):
        return ['%s.%s' % (role.organisation.name, role.name) for role in bundle.obj.roles.all()]

    def dehydrate_saml_organisations(self, bundle):
        return [str(org.id) for org in bundle.obj.organisations.all()]

    def dehydrate_saml_roles(self, bundle):
        return [role.code for role in bundle.obj.roles.all()]

    def dehydrate_saml_permissions(self, bundle):
        perms = []
        for role in bundle.obj.roles.all():
            perms += role.permission_codes
        return perms

    def obj_get(self, request=None, **kwargs):
        from django.contrib.auth import authenticate
        user = authenticate(
            username=request.GET.get('username', None),
            password=request.GET.get('password', None))
        if user:
            return self._meta.queryset.get(pk=user)
        raise ImmediateHttpResponse(HttpResponse(status=401))

    @property
    def urls(self):
        from django.conf.urls.defaults import patterns, url
        urlpatterns = patterns('',
            url(r'^(?P<resource_name>%s)/$' % self._meta.resource_name, self.wrap_view('dispatch_detail'), name='api_dispatch_detail'),
        )
        return urlpatterns

    class Meta(BaseResource.Meta):
        queryset = User.objects.all().select_related()
        fields = ('id', 'username', 'first_name', 'last_name',)
