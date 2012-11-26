
from django.contrib import admin
import models
import django.contrib.auth.models

class PermissionAdmin(admin.ModelAdmin):
  pass


class OrganisationAdmin(admin.ModelAdmin):
  list_display = ('name', 'title', 'user_count')

  def user_count(self, obj):
    return obj.user_set.count()


class GroupAdmin(admin.ModelAdmin):
  list_display = ('name', 'title', 'organisation', 'user_count')
  list_filter = ('organisation',)

  def user_count(self, obj):
    return obj.user_set.count()


class RoleAdmin(admin.ModelAdmin):
  list_display = ('name', 'title', 'organisation', 'user_count')
  list_filter = ('organisation',)

  def user_count(self, obj):
    return obj.user_set.count()


class UserAdmin(admin.ModelAdmin):
  list_display = ('username', 'phone_number', 'theme_color', 'picture_url', 'role_list', 'organisation_list', 'group_list')
  search_fields = ['username', 'first_name', 'last_name'] 
  list_filter = ('organisations', 'roles', 'groups')
  list_per_page = 50

  def role_list(self, obj):
    return ', '.join([unicode(o) for o in obj.roles.all()])

  def organisation_list(self, obj):
    return ', '.join([unicode(o) for o in obj.organisations.all()])

  def group_list(self, obj):
    return ', '.join([unicode(o) for o in obj.groups.all()])


class ServicePermissionAdmin(admin.ModelAdmin):
  list_display = ('name', 'service', 'entity', 'action')


try:
  admin.site.register(django.contrib.auth.models.Permission)
except:
  pass
admin.site.register(models.Organisation, OrganisationAdmin)
admin.site.register(models.Group, GroupAdmin)
admin.site.register(models.Role, RoleAdmin)
admin.site.register(models.ServicePermission, ServicePermissionAdmin)
admin.site.register(models.User, UserAdmin)

