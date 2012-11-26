# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting model 'User'
        db.delete_table('dreamuserdb_user')

        # Removing M2M table for field organisations on 'User'
        db.delete_table('dreamuserdb_user_organisations')

        # Removing M2M table for field groups on 'User'
        db.delete_table('dreamuserdb_user_groups')

        # Removing M2M table for field roles on 'User'
        db.delete_table('dreamuserdb_user_roles')


    def backwards(self, orm):
        
        # Adding model 'User'
        db.create_table('dreamuserdb_user', (
            ('phone_number', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('_username', self.gf('django.db.models.fields.CharField')(max_length=30, null=True)),
            ('_email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True)),
            ('_first_name', self.gf('django.db.models.fields.CharField')(max_length=30, null=True)),
            ('_last_name', self.gf('django.db.models.fields.CharField')(max_length=30, null=True)),
            ('password_md5', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], unique=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('theme_color', self.gf('django.db.models.fields.CharField')(default='ffffff', max_length=8, null=True, blank=True)),
            ('picture_url', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('dreamuserdb', ['User'])

        # Adding M2M table for field organisations on 'User'
        db.create_table('dreamuserdb_user_organisations', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('user', models.ForeignKey(orm['dreamuserdb.user'], null=False)),
            ('organisation', models.ForeignKey(orm['dreamuserdb.organisation'], null=False))
        ))
        db.create_unique('dreamuserdb_user_organisations', ['user_id', 'organisation_id'])

        # Adding M2M table for field groups on 'User'
        db.create_table('dreamuserdb_user_groups', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('user', models.ForeignKey(orm['dreamuserdb.user'], null=False)),
            ('group', models.ForeignKey(orm['dreamuserdb.group'], null=False))
        ))
        db.create_unique('dreamuserdb_user_groups', ['user_id', 'group_id'])

        # Adding M2M table for field roles on 'User'
        db.create_table('dreamuserdb_user_roles', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('user', models.ForeignKey(orm['dreamuserdb.user'], null=False)),
            ('role', models.ForeignKey(orm['dreamuserdb.role'], null=False))
        ))
        db.create_unique('dreamuserdb_user_roles', ['user_id', 'role_id'])


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'dreamuserdb.group': {
            'Meta': {'unique_together': "(('name', 'organisation'),)", 'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'official': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'organisation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dreamuserdb.Organisation']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'dreamuserdb.olduser': {
            'Meta': {'object_name': 'OldUser'},
            '_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True'}),
            '_first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True'}),
            '_last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True'}),
            '_username': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['dreamuserdb.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'organisations': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['dreamuserdb.Organisation']", 'symmetrical': 'False', 'blank': 'True'}),
            'password_md5': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'picture_url': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'roles': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['dreamuserdb.Role']", 'symmetrical': 'False', 'blank': 'True'}),
            'theme_color': ('django.db.models.fields.CharField', [], {'default': "'ffffff'", 'max_length': '8', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
        'dreamuserdb.organisation': {
            'Meta': {'object_name': 'Organisation'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'dreamuserdb.role': {
            'Meta': {'unique_together': "(('name', 'organisation'),)", 'object_name': 'Role'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'official': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'organisation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dreamuserdb.Organisation']"}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['dreamuserdb.ServicePermission']", 'symmetrical': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'dreamuserdb.servicepermission': {
            'Meta': {'object_name': 'ServicePermission'},
            'action': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'entity': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'service': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['dreamuserdb']
